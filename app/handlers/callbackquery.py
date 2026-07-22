from aiogram.filters import callback_data
from aiogram.types import CallbackQuery
from aiogram import Router
from app.handlers.order import router as order_handler
from app.handlers.start import router as start_message

router = Router()
@router.callback_query()
async def callback(message: CallbackQuery):
    if callback_data == 'order':
        order_handler.order()
    elif callback_data == 'photoshoot':
        await message.answer(text='Продолжительность съёмки — от 1 до 4 часов.\n\n'
                                  'Стоимость:'
                                  '750 руб./час — при согласии на использование фотографий в моём портфолио.'
                                  '850 руб./час — без согласия на публикацию фотографий.\n\n'
                                  'Полная предоплата')
    elif callback_data == 'event':
        await message.answer(text='Стоимость:\n'
                                  '800 руб./час — при согласии на использование фотографий в моём портфолио.'
                                  '950 руб./час — без согласия на публикацию фотографий.\n\n'
                                  'Полная предоплата.\n'
                                  'При съёмке продолжительностью более 4 часов также необходим перерыв, который входит в рабочее время (время съёмки не приостанавливается).'
                                  'Перед съёмкой необходимо заранее обсудить объём, формат работы и ваши пожелания.')
    elif callback_data == 'cancel':
        order_handler()
    elif callback_data == 'faq':
        await message.answer(text='Ответы на частые вопросы:\n')