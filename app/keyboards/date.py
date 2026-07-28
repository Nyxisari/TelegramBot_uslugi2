from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def days_keyboard(free_days: list[int], month_name: str) -> InlineKeyboardMarkup:
    """
    Строит инлайн-клавиатуру со свободными днями месяца.
    callback_data формата 'day:<Месяц>:<день>' - удобно парсить в хендлере записи.
    """
    keyboard_days = [
        InlineKeyboardButton(text=str(day), callback_data=f"day:{month_name}:{day}")
        for day in free_days
    ]
    keyboard_rows = [keyboard_days[x:x + 5] for x in range(0, len(keyboard_days), 5)]
    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)