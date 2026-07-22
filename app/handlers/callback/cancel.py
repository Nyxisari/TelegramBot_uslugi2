from aiogram import Router, F
from aiogram.types import CallbackQuery
from handlers.start import router as start
from handlers.callback.event import router as event
from handlers.callback.photoshoot import router as photoshoot

router = Router()

@router.callback_query(F.data == 'cancel_faq')
async def faq(callback: CallbackQuery):
    router.include_router(start)
@router.callback_query(F.data == 'cancel_event')
async def event(callback: CallbackQuery):
        router.include_router(event)
@router.callback_query(F.data == 'cancel_photoshoot')
async def photoshoot(callback: CallbackQuery):
    router.include_router(photoshoot)