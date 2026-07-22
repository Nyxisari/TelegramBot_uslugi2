from aiogram import Router
from handlers.callback.order import router as order_handler
from handlers.callback.faq import router as faq_handler

router = Router()

router.include_router(order_handler)
router.include_router(faq_handler)
