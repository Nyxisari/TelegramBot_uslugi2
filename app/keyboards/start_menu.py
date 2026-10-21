from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard_start = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Заказать', callback_data='order')],
    [InlineKeyboardButton(text='Портфолио', url='https://t.me/u3pPhoto'),
    InlineKeyboardButton(text='Отзывы', url='https://t.me/NyxiPhotoReviews')],
    [InlineKeyboardButton(text='FAQ', callback_data='faq')]
], resize_keyboard=True)