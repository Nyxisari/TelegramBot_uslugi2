from aiogram import Router, F
from aiogram.types import CallbackQuery

from handlers.start import start as start_handler
from handlers.callback.event import event as event_handler
from handlers.callback.order import order as order_handler

router = Router()


@router.callback_query(F.data.startswith("cancel:"))
async def cancel(callback: CallbackQuery):
    _, type_cancel = callback.data.split(':')

    if type_cancel == "start":
        await start_handler(callback.message)
        await callback.answer()
    elif type_cancel == "order":
        await order_handler(callback)
    else:
        await callback.answer()