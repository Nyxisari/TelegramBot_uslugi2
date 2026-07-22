from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.cancel import cancel_photoshoot

router = Router()

text_msg=("*Условия фотосессии*\n\n"
        "🕐 *Продолжительность съёмки* - от 1 до 4 часов.\n\n"
        "💲 *Стоимость*:\n"
        "- 750 руб./час - при согласии на использование фотографий в моём портфолио.\n"
        "- 850 руб./час - без согласия на публикацию фотографий.\n\n"
        "🛡️ *Предоплата* - полная\n\n"
        "личные сообщения: @NyxiPhoto")

@router.callback_query(F.data == 'photoshoot')
async def photoshoot(callback: CallbackQuery):
    await callback.message.answer(
        text=text_msg,
        reply_markup=cancel_photoshoot, parse_mode='Markdown'
    )
    await callback.answer()
