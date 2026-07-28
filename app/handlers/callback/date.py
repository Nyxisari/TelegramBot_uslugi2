from aiogram import Router, F
from aiogram.types import CallbackQuery

from handlers.callback.Google_sheet.gsheet import get_free_days
from keyboards.date import days_keyboard

router = Router()

# Список названий месяцев - должен совпадать с ключами в gsheet.add_month
MONTH_NAMES = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
]


@router.callback_query(F.data.in_(MONTH_NAMES))
async def show_free_days(callback: CallbackQuery):
    month_name = callback.data
    free_days = await get_free_days(month_name)

    if not free_days:
        await callback.message.answer(f"На {month_name} свободных дней нет 😔")
        await callback.answer()
        return

    await callback.message.answer(
        text=f"📅 Свободные дни в {month_name}:",
        reply_markup=days_keyboard(free_days, month_name)
    )
    await callback.answer()