from aiogram import Router

from handlers.callback.order import router as order_handler
from handlers.callback.faq import router as faq_handler
from handlers.callback.photoshoot import router as photoshoot_handler
from handlers.callback.event import router as event_handler
from handlers.callback.cancel import router as cancel_handler

router = Router()

router.include_router(order_handler)
router.include_router(faq_handler)
router.include_router(photoshoot_handler)
router.include_router(event_handler)
