from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.cancel import cancel_event

router = Router()

text_msg=("*Условия съёмки мероприятий*\n\n"
        "💲 *Стоимость*:\n"
        "- *800 руб./час* - при согласии на использование фотографий в моём портфолио.\n"
        "- *950 руб./час* - без согласия на публикацию фотографий.\n\n"
        "🛡️ *Предоплата* - полная\n\n"
        "🍱При съёмке продолжительностью более 4 часов также необходим перерыв,\nкоторый входит в рабочее время (время съёмки не приостанавливается).\n"
        "📄Перед съёмкой необходимо заранее обсудить объём, формат работы и ваши пожелания в личных сообщениях: @NyxiPhoto")

@router.callback_query(F.data == 'event')
async def event(callback: CallbackQuery):
    await callback.message.answer(
        text=text_msg,
        reply_markup=cancel_event, parse_mode='Markdown'
    )
    await callback.answer()