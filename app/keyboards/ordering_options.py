from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_options = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Фотосессия', callback_data='photoshoot'),
    InlineKeyboardButton(text='Интерьерная съёмка', callback_data='event')],
    [InlineKeyboardButton(text='Назад', callback_data='cancel:start')],
], resize_keyboard=True)