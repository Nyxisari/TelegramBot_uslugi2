from config import settings

import asyncio
import logging
from aiogram import Bot, Dispatcher

from handlers.start import router as start_router
from handlers.callbacks import router as callback_query
from handlers.callback.Google_sheet.gsheet import release_all_reserved

async def main():
    logging.basicConfig(level=logging.INFO)

    # После перезапуска броней в памяти нет - снимаем зависшие "резервировано ..." в таблице
    try:
        released = await release_all_reserved()
        logging.info("Снято зависших броней: %s", released)
    except Exception:
        logging.exception("Не удалось очистить зависшие брони")

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(callback_query)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
