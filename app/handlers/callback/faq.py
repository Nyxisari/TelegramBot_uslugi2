from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.cancel import cancel_faq

router = Router()

@router.callback_query(F.data == 'faq')
async def faq(callback: CallbackQuery):
    await callback.message.answer(
        text="❓ Часто задаваемые вопросы:\n\n"
             "1. Как сделать заказ? - Просто нажмите кнопку заказать и выберите дату и время\n"
             "2. Как оплатить услугу? - Идите по инструкции бота.\n"
             "3. Как связаться с поддержкой? - можете написать @Nyxiphoto",
        reply_markup=cancel_faq
    )
    await callback.answer()
