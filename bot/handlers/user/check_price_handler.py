import asyncio
import datetime
from urllib.parse import urlparse

from aiogram import Router, Bot

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from database.repositories import (user as user_repo,
                                   product as product_repo,
                                   user_product as user_product_repo,
                                   price_log as price_log_repo,
                                   check_interval as check_interval_repo)
from database.models import PriceLog
from bot.handlers.user.menu_handler import get_title_and_price_info

checker = Router()


async def update_product_prices_in_hour(bot: Bot):
    print(f"Обновление прайс-листа...")
    users_id = await check_interval_repo.get_users_by_interval(1)
    ten_hours_ago = datetime.datetime.now() - datetime.timedelta(seconds=60)
    for user_id in users_id:
        products = await product_repo.get_user_products(user_id)

        is_changed = False
        news_text = ""

        for product in products:
            last_log: PriceLog = await price_log_repo.get_last_log_by_product_id(product.id)
            if True:
                print("Проверка прайс-листа")
                driver = webdriver.Chrome()
                driver.get(product.url)
                title, price = await get_title_and_price_info(product.url, driver)

                if product.price != price:
                    is_changed = True
                    await price_log_repo.add_price_log(product.id, price)
                    await product_repo.change_product_price(product.id, price)

                    shift_symbol = "📉"
                    if product.price < price:
                        shift_symbol = "📈"

                    news_text = (f"{news_text}\n\n"
                                 f"Товар: {title}\n"
                                 f"Цена: {price} {shift_symbol}\n"
                                 f"Было: {product.price} -> Стало: {price}\n"
                                 f"Имя магазина: {urlparse(product.url).netloc}\n"
                                 f"Ссылка: {product.url}")

                driver.quit()
            # else:
            #     penultimate_log = await price_log_repo.get_penultimate_log_by_product_id(product.id)
            #     if penultimate_log is not None and penultimate_log.price != last_log.price:
            #         is_changed = True
            #         shift_symbol = "📉"
            #         if penultimate_log.price < last_log.price:
            #             shift_symbol = "📈"
            #
            #         news_text = (f"{news_text}\n\n"
            #                      f"Товар: {title}\n"
            #                      f"Цена: {price} {shift_symbol}\n"
            #                      f"Было: {product.price} -> Стало: {price}\n"
            #                      f"Имя магазина: {urlparse(product.url).netloc}\n"
            #                      f"Ссылка: {product.url}")
        if is_changed:
            await bot.send_message(chat_id=user_id, text=news_text)
        else:
            await bot.send_message(chat_id=user_id, text="Ничего не изменилось!")


async def update_product_prices_in_10_hours(bot: Bot):
    print(f"Обновление прайс-листа...")
    users_id = await check_interval_repo.get_users_by_interval(10)
    ten_hours_ago = datetime.datetime.now() - datetime.timedelta(seconds=60)
    for user_id in users_id:
        products = await product_repo.get_user_products(user_id)

        is_changed = False
        news_text = ""

        for product in products:
            last_log: PriceLog = await price_log_repo.get_last_log_by_product_id(product.id)
            if last_log.timestamp >= ten_hours_ago:
                driver = webdriver.Chrome()
                driver.get(product.url)
                title, price = await get_title_and_price_info(product.url, driver)

                if product.price != price:
                    is_changed = True
                    await price_log_repo.add_price_log(product.id, price)
                    await product_repo.change_product_price(product.id, price)

                    shift_symbol = "📉"
                    if product.price < price:
                        shift_symbol = "📈"

                    news_text = (f"{news_text}\n\n"
                                 f"Товар: {title}\n"
                                 f"Цена: {price} {shift_symbol}\n"
                                 f"Было: {product.price} -> Стало: {price}")
                driver.quit()

            else:
                penultimate_log = await price_log_repo.get_penultimate_log_by_product_id(product.id)
                if penultimate_log is not None:
                    is_changed = True
                    shift_symbol = "📉"
                    if penultimate_log.price < last_log.price:
                        shift_symbol = "📈"

                    news_text = (f"{news_text}\n\n"
                                 f"Товар: {product.name}\n"
                                 f"Цена: {product.price} {shift_symbol}\n"
                                 f"Было: {penultimate_log.price} -> Стало: {product.price}")
        if is_changed:
            await bot.send_message(chat_id=user_id, text=news_text)
        else:
            await bot.send_message(chat_id=user_id, text="Ничего не изменилось!")

async def update_product_prices_in_24_hours(bot: Bot):
    pass
