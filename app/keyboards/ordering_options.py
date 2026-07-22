from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_options = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Фотосессия', callback_data='photoshoot'),
    InlineKeyboardButton(text='Мероприятие', callback_data='event')],
    [InlineKeyboardButton(text='Назад', callback_data='cancel_order')],
], resize_keyboard=True)