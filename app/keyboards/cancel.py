from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

cancel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='cancel')],
], resize_keyboard=True)