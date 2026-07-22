from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from app.keyboards.ordering_options import keyboard_options

router = Router()

@router.message(Message)
async def order(message: Message):
    await message.answer(text='Выбирите что вам нужно', reply_markup=keyboard_options)