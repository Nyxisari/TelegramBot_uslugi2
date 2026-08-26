from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.ordering_options import keyboard_options

router = Router()

@router.callback_query(F.data == 'order')
async def order(callback: CallbackQuery):
    await callback.message.answer(
        text='Выберите вид съёмки.',
        reply_markup=keyboard_options
    )
    await callback.answer()