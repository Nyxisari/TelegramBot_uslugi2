from config import settings

import asyncio
from aiogram import Bot, Dispatcher

from handlers.start import router as start_router
from handlers.callbacks import router as callback_query
from handlers.callback.cancel import router as cancel_router

async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(callback_query)
    dp.include_router(cancel_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())