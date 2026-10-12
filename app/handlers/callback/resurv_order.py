from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from handlers.callback.Google_sheet.gsheet import get_free_times
from keyboards.times import times_keyboard
from keyboards.confirm import confirm_keyboard

from handlers.yookassa import start_payment

router = Router()

MAX_HOURS_IN_A_ROW = 4  # соответствует условиям фотосессии: "от 1 до 4 часов"


@router.callback_query(F.data.startswith("day:"))
async def show_free_times(callback: CallbackQuery, state: FSMContext):
    """Пользователь выбрал день -> показываем доступное время этого дня, сбрасываем прошлый выбор."""
    _, month_name, day = callback.data.split(":")
    await state.update_data(selected=[])

    free_times = await get_free_times(month_name, day)

    if not free_times:
        await callback.message.answer(f"На {day} {month_name.lower()} свободного времени нет 😔")
        await callback.answer()
        return

    await callback.message.answer(
        text=f"🕐 Выберите время на {day} {month_name.lower()} (можно несколько часов подряд):",
        reply_markup=times_keyboard(free_times, month_name, day, selected=[])
    )
    await callback.answer()


@router.callback_query(F.data.startswith("toggle:"))
async def toggle_time(callback: CallbackQuery, state: FSMContext):
    """Пользователь нажал на конкретный час -> добавляем/убираем его из выбора."""
    _, month_name, day, index, label = callback.data.split(":", 4)
    index = int(index)

    data = await state.get_data()
    selected = list(data.get("selected", []))

    if index in selected:
        # снимаем выбор - разрешаем только с края, чтобы не рвать диапазон
        if index == min(selected) or index == max(selected):
            selected.remove(index)
        else:
            await callback.answer(
                "Можно снимать только крайний час выбора, чтобы часы оставались подряд.",
                show_alert=True
            )
            return
    else:
        if not selected:
            selected.append(index)
        elif index == min(selected) - 1 or index == max(selected) + 1:
            if len(selected) >= MAX_HOURS_IN_A_ROW:
                await callback.answer(f"Максимум {MAX_HOURS_IN_A_ROW} часа подряд.", show_alert=True)
                return
            selected.append(index)
        else:
            await callback.answer("Можно выбирать только часы, идущие подряд.", show_alert=True)
            return

    await state.update_data(selected=selected)

    free_times = await get_free_times(month_name, day)
    await callback.message.edit_reply_markup(
        reply_markup=times_keyboard(free_times, month_name, day, selected=selected)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("reset:"))
async def reset_selection(callback: CallbackQuery, state: FSMContext):
    """Сбросить текущий выбор часов."""
    _, month_name, day = callback.data.split(":")
    await state.update_data(selected=[])

    free_times = await get_free_times(month_name, day)
    await callback.message.edit_reply_markup(
        reply_markup=times_keyboard(free_times, month_name, day, selected=[])
    )
    await callback.answer()


@router.callback_query(F.data.startswith("done:"))
async def show_order_confirmation(callback: CallbackQuery, state: FSMContext):
    """Пользователь нажал "Готово" -> показываем сводку заказа и просим подтвердить."""
    _, month_name, day = callback.data.split(":")

    data = await state.get_data()
    selected = sorted(data.get("selected", []))

    if not selected:
        await callback.answer("Сначала выберите хотя бы один час.", show_alert=True)
        return

    free_times = dict(await get_free_times(month_name, day))  # index -> label
    labels = [free_times[i] for i in selected if i in free_times]

    text = (
        "📋 *Подтверждение записи*\n\n"
        f"📅 Дата: {day} {month_name}\n"
        f"🕐 Время: {', '.join(labels)} ({len(labels)} ч.)\n"
        f"👤 От: @{callback.from_user.username}\n\n"
        "Всё верно?"
    )

    await callback.message.answer(
        text=text,
        reply_markup=confirm_keyboard(month_name, day),
        parse_mode='Markdown'
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm:"))
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    """Пользователь подтвердил -> временно резервируем выбранные часы в таблице
    ('резервировано @username') и сразу выставляем счёт ЮKassa. Если за 5 минут оплаты нет -
    бронь снимается и время снова свободно (см. handlers/yookassa.py)."""
    _, month_name, day = callback.data.split(":")

    username = callback.from_user.username
    if not username:
        await callback.answer(
            "У вас не задан username в Telegram — установите его в настройках, чтобы записаться.",
            show_alert=True
        )
        return

    data = await state.get_data()
    selected = sorted(data.get("selected", []))

    if not selected:
        await callback.answer("Выбор времени потерялся, начните заново.", show_alert=True)
        return

    # сбрасываем выбор сразу: повторное нажатие "Подтвердить" не создаст вторую бронь
    await state.update_data(selected=[])
    await callback.answer()

    error = await start_payment(callback.bot, callback.from_user, callback.message.chat.id,
                                month_name, day, selected)
    if error:
        await callback.message.edit_text(f"⚠️ {error}")
    else:
        await callback.message.edit_text("✅ Время зарезервировано на 5 минут. Оплатите счёт ниже.")


@router.callback_query(F.data == "cancel_reserv_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    await state.update_data(selected=[])
    await callback.message.edit_text("Запись отменена.")
    await callback.answer()