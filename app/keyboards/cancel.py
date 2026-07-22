from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

cancel_event = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='cancel_event')],
], resize_keyboard=True)
cancel_faq = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='cancel_faq')],
], resize_keyboard=True)
cancel_photoshoot = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='cancel_photoshoot')],
], resize_keyboard=True)