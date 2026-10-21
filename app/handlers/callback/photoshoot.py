from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.months import months_names
router = Router()

text_msg=("*Условия фотосессии*\n\n"
        "🕐 *Продолжительность съёмки* - от 1 до 4 часов.\n\n"
        "💲 *Стоимость*:\n"
        "- 1500 руб./час.\n\n"
        "🛡️ *Предоплата* - полная\n\n"
        "личные сообщения: @NyxiPhoto")

@router.callback_query(F.data == 'photoshoot')
async def photoshoot(callback: CallbackQuery):
    await callback.message.answer(
        text=text_msg,
        reply_markup=await months_names(), parse_mode='Markdown'
    )
    await callback.answer()
