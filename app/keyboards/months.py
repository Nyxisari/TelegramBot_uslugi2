import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.callback.Google_sheet.gsheet import get_free_months


async def months_names():
    """Клавиатура месяцев: только те листы, где есть хотя бы один свободный слот.
    callback_data кнопки = название месяца (его ловит handlers/callback/date.py)."""
    try:
        months = await get_free_months()
    except Exception:
        logging.exception("Не удалось получить список месяцев из таблицы")
        months = []
    keyboard_date = [InlineKeyboardButton(text=x, callback_data=x) for x in months]
    keyboard_rows = [keyboard_date[x:x+4] for x in range(0, len(keyboard_date), 4)]
    keyboard_rows.append([InlineKeyboardButton(text="Отмена", callback_data="cancel:order")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows, resize_keyboard=True)
    return keyboard
