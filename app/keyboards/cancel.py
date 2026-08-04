from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

cancel_event = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='cancel:event')],
], resize_keyboard=True)
cancel_faq = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='cancel:faq')],
], resize_keyboard=True)