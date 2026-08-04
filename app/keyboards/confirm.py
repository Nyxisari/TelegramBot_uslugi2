from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def confirm_keyboard(month_name: str, day) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm:{month_name}:{day}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_reserv_order")],
    ])