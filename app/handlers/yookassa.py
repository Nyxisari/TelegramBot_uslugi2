import asyncio
import json
import logging
from dataclasses import dataclass, field

from aiogram import Bot, F, Router
from aiogram.types import (CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup,
                           LabeledPrice, Message, PreCheckoutQuery, User)

from config import settings
from handlers.callback.Google_sheet.gsheet import finalize_booking, release_slots, reserve_slots

router = Router()

RESERVE_TIMEOUT = 5 * 60  # сколько живёт бронь без оплаты, сек
PAID_GRACE = 90           # после открытия формы оплаты (pre_checkout) даём ещё немного времени


@dataclass
class Reservation:
    user_id: int
    chat_id: int
    month: str
    day: str
    indices: list[int]
    labels: list[str]
    display_name: str
    payload: str
    total: int                      # в копейках
    invoice_message_id: int | None = None
    paying: bool = False            # пользователь уже открыл форму оплаты
    task: asyncio.Task | None = field(default=None, repr=False)


# user_id -> активная бронь (одна на пользователя). Живёт в памяти процесса;
# зависшие после перезапуска брони чистит gsheet.release_all_reserved() при старте.
reservations: dict[int, Reservation] = {}
_starting: set[int] = set()  # защита от двойного нажатия "Подтвердить"


def display_name_of(user: User) -> str:
    return f"@{user.username}" if user.username else f"id{user.id}"


def has_reservation(user_id: int) -> bool:
    return user_id in reservations or user_id in _starting


async def _safe_release(res: Reservation) -> None:
    try:
        await release_slots(res.month, res.day, res.indices, res.display_name)
    except Exception:
        logging.exception("Не удалось освободить слоты %s", res)


async def _drop_invoice(bot: Bot, res: Reservation, text: str) -> None:
    if res.invoice_message_id:
        try:
            await bot.delete_message(res.chat_id, res.invoice_message_id)
        except Exception:
            pass
    try:
        await bot.send_message(res.chat_id, text)
    except Exception:
        logging.exception("Не удалось отправить сообщение пользователю %s", res.user_id)


def _schedule_expire(bot: Bot, res: Reservation, delay: float) -> None:
    if res.task and not res.task.done():
        res.task.cancel()
    res.task = asyncio.create_task(_expire(bot, res.user_id, delay))


async def _expire(bot: Bot, user_id: int, delay: float) -> None:
    await asyncio.sleep(delay)
    res = reservations.pop(user_id, None)
    if res is None:
        return
    await _safe_release(res)
    await _drop_invoice(bot, res, "⌛ Время оплаты истекло, бронь снята. Нажмите /start, чтобы выбрать время заново.")


async def start_payment(bot: Bot, user: User, chat_id: int, month: str, day,
                        indices: list[int]) -> str | None:
    """Резервирует слоты в таблице ('резервировано @username') и отправляет счёт.
    Возвращает None при успехе, иначе текст ошибки для пользователя."""
    if has_reservation(user.id):
        return "У вас уже есть неоплаченная бронь. Оплатите её или отмените."

    _starting.add(user.id)
    try:
        name = display_name_of(user)
        try:
            labels, unavailable = await reserve_slots(month, day, indices, name)
        except Exception:
            logging.exception("reserve_slots failed")
            return "Не удалось связаться с таблицей. Попробуйте чуть позже."
        if unavailable:
            return f"Это время уже занято: {', '.join(unavailable)}. Выберите другое время."

        count = len(indices)
        res = Reservation(
            user_id=user.id, chat_id=chat_id, month=month, day=str(day),
            indices=list(indices), labels=list(labels), display_name=name,
            payload=f"ps_{user.id}", total=settings.PRICE * count,
        )
        reservations[user.id] = res

        provider_data = {
            "receipt": {
                "items": [{
                    "description": "Бронирование фотосессии (1 час)",
                    "quantity": f"{count}.00",
                    "amount": {
                        "value": f"{settings.PRICE / 100:.2f}",
                        "currency": "RUB",
                    },
                    "vat_code": 1,  # 1 = НДС не облагается (для самозанятых)
                }]
            }
        }
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить", pay=True)],
            [InlineKeyboardButton(text="❌ Отменить бронь", callback_data="cancel_pay")],
        ])
        try:
            msg = await bot.send_invoice(
                chat_id=chat_id,
                title="Фотосессия",
                description=f"{day} {month}, время: {', '.join(labels)}. Бронь удерживается 5 минут.",
                payload=res.payload,
                provider_token=settings.YOOKASSA_TOKEN,
                currency="RUB",
                prices=[LabeledPrice(label=f"Фотосессия, {count} ч.", amount=res.total)],
                provider_data=json.dumps(provider_data),
                reply_markup=markup,
            )
        except Exception:
            logging.exception("send_invoice failed")
            reservations.pop(user.id, None)
            await _safe_release(res)
            return "Не удалось выставить счёт. Попробуйте ещё раз."

        res.invoice_message_id = msg.message_id
        _schedule_expire(bot, res, RESERVE_TIMEOUT)
        return None
    finally:
        _starting.discard(user.id)


@router.callback_query(F.data == "cancel_pay")
async def cancel_payment_handler(callback: CallbackQuery):
    res = reservations.get(callback.from_user.id)
    if res is None:
        await callback.answer("Бронь уже снята", show_alert=True)
        return
    if res.paying:
        await callback.answer("Оплата уже обрабатывается, подождите минуту.", show_alert=True)
        return
    reservations.pop(callback.from_user.id, None)
    if res.task:
        res.task.cancel()
    await _safe_release(res)
    await callback.answer()
    await _drop_invoice(callback.bot, res, "Бронь отменена. Нажмите /start, чтобы выбрать время заново.")


@router.pre_checkout_query()
async def checkout_handler(query: PreCheckoutQuery):
    res = reservations.get(query.from_user.id)
    if res is None or query.invoice_payload != res.payload or query.total_amount != res.total:
        await query.answer(ok=False, error_message="Время оплаты истекло, бронь снята. Выберите время заново (/start).")
        return
    # форма оплаты открыта: не снимаем бронь посреди платежа, но и не держим вечно
    res.paying = True
    _schedule_expire(query.bot, res, PAID_GRACE)
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    payment = message.successful_payment
    payment_id = payment.telegram_payment_charge_id
    logging.info("Оплата: %s", payment)

    res = reservations.pop(message.from_user.id, None)
    if res is None:
        logging.error("Оплата без активной брони: user=%s payment=%s", message.from_user.id, payment_id)
        await message.answer(
            f"Оплата получена, но бронь уже была снята. Напишите администратору, id платежа: {payment_id}")
        return
    if res.task:
        res.task.cancel()

    try:
        ok = await finalize_booking(res.month, res.day, res.indices, res.display_name)
    except Exception:
        logging.exception("finalize_booking failed")
        ok = False

    if ok:
        await message.answer(
            f"Оплата прошла успешно! id: {payment_id}\n"
            f"Вы записаны: {res.day} {res.month}, время: {', '.join(res.labels)}.")
    else:
        logging.error("Не удалось записать оплаченную бронь %s, payment=%s", res, payment_id)
        await message.answer(
            f"Оплата прошла, но записать время в таблицу не получилось. "
            f"Напишите администратору, id платежа: {payment_id}")
