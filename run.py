import os
import logging
import asyncio

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv

from database.app_db_context import async_main
from bot.handlers.user import user, menu
from bot.handlers.user.check_price_handler import *


async def main():
    await async_main()
    load_dotenv()
    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher()
    dp.include_routers(user, menu, checker)

    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.add_job(update_product_prices_in_hour, trigger='interval', seconds=90, kwargs={'bot': bot})
    scheduler.add_job(update_product_prices_in_10_hours, trigger='interval', minutes=30, kwargs={'bot': bot})
    scheduler.add_job(update_product_prices_in_24_hours, trigger='interval', hours=1, kwargs={'bot': bot})
    scheduler.start()
    # dp.include_router(admin)
    await dp.start_polling(bot)
    # await update_product_prices_in_hour(bot)


if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO)
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
