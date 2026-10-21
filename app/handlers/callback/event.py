from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.months import months_names

router = Router()

text_msg=("*Условия съёмки интерьера*\n\n"
        "💲 *Стоимость*:\n"
        "- 10000 руб. за услугу.\n\n"
        "🛡️ *Предоплата* - полная\n\n"
        "📄Перед съёмкой необходимо заранее обсудить объём, формат работы и ваши пожелания в личных сообщениях: @NyxiPhoto")

@router.callback_query(F.data == 'event')
async def event(callback: CallbackQuery):
    await callback.message.answer(
        text=text_msg,
        reply_markup=await months_names(), parse_mode='Markdown'
    )
    await callback.answer()