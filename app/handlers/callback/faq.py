from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.cancel import cancel

router = Router()

@router.callback_query(F.data == 'faq')
async def faq(callback: CallbackQuery):
    await callback.message.answer(
        text="❓ Часто задаваемые вопросы:\n\n"
             "1. Как сделать заказ?\n"
             "2. Как оплатить услугу?\n"
             "3. Как связаться с поддержкой?",
        reply_markup=cancel
    )
    await callback.answer()