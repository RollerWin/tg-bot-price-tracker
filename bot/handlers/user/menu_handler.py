import requests
from bs4 import BeautifulSoup
import asyncio
import time
import os
import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from urllib.parse import urlparse

from database.repositories import (user as user_repo,
                                   product as product_repo,
                                   user_product as user_product_repo,
                                   price_log as price_log_repo,
                                   check_interval as check_interval_repo)
from bot.keyboards import menu_keyboards as menu_kb
from bot.keyboards import util_keyboards as util_kb
from bot.handlers.user import write_info
from bot_config import CSSParser

menu = Router()


class Products(StatesGroup):
    add_product = State()
    catalog = State()
    product_info = State()
    change_interval = State()


@menu.callback_query(F.data == 'new_product')
async def add_product_callback(call: CallbackQuery, state: FSMContext):
    await state.set_state(Products.add_product)
    await call.message.answer("Введите ссылку на товар", reply_markup=util_kb.back)


@menu.callback_query(Products.add_product, F.data == 'back')
async def deny_add_product(call: CallbackQuery, state: FSMContext):
    await state.clear()
    user_info = await user_repo.get_user_info(call.from_user.id)
    await call.message.answer(await write_info(user_info), reply_markup=menu_kb.main_menu)


@menu.message(Products.add_product)
async def show_product_callback(message: Message, state: FSMContext):
    await state.set_state(Products.add_product)
    # proxy = os.getenv("PROXY")

    # chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Запуск в фоновом режиме
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox")

    url = message.text
    desired_product = await product_repo.is_product_already_exist(url)
    user_id = await user_repo.get_user_id(message.from_user.id)

    if desired_product is None:
        driver = webdriver.Chrome()
        driver.get(url)

        try:
            title, price = await get_title_and_price_info(url, driver)
            await product_repo.add_product(title, price, url)

            added_product = await product_repo.get_product_id_by_name(title)

            await user_product_repo.add_product_to_user_relation(user_id, added_product.id)
            await price_log_repo.add_price_log(added_product.id, price)
            await message.answer("Товар добавлен!", reply_markup=menu_kb.main_menu)
        except Exception as e:
            await message.answer(f"Ошибка при получении данных: {str(e)}", reply_markup=menu_kb.main_menu)
            driver.quit()
            return

        driver.quit()
    else:
        desired_product_id = desired_product.id
        result = await user_product_repo.is_relation_exist(user_id, desired_product_id)
        print(result)

        if result is None:
            await user_product_repo.add_product_to_user_relation(user_id, desired_product.id)
            await message.answer("Товар добавлен!", reply_markup=menu_kb.main_menu)
        else:
            await message.answer("Товар уже добавлен!", reply_markup=menu_kb.main_menu)

    await state.clear()


@menu.callback_query(F.data == 'catalog')
async def catalog_callback(call: CallbackQuery, state: FSMContext):
    await state.set_state(Products.catalog)
    await call.message.answer("Все ваши отслеживаемые товары на данный момент",
                                 reply_markup=await menu_kb.get_products_keyboard(call.from_user.id))


@menu.callback_query(Products.catalog, F.data == 'back')
async def deny_catalog(call: CallbackQuery, state: FSMContext):
    await state.clear()
    user_info = await user_repo.get_user_info(call.from_user.id)
    await call.message.answer(await write_info(user_info), reply_markup=menu_kb.main_menu)


@menu.callback_query(Products.catalog, F.data.startswith('product_'))
async def product_info_callback(call: CallbackQuery, state: FSMContext):
    await state.set_state(Products.product_info)
    product_id = int(call.data.split("_")[1])
    await state.update_data(product_id=product_id)
    current_product = await product_repo.get_product_by_id(product_id)
    await call.message.answer(f"Название: {current_product.name}\n"
                                 f"Цена: {current_product.price}\n"
                                 f"Ссылка: {current_product.url}\n"
                                 f"В наличии: {current_product.is_available}",
                                 reply_markup=menu_kb.product_info_menu
                                 )


@menu.callback_query(Products.product_info, F.data == 'back')
async def deny_product_info(call: CallbackQuery, state: FSMContext):
    await state.set_state(Products.catalog)
    await call.message.answer("Все ваши отслеживаемые товары на данный момент",
                                 reply_markup=await menu_kb.get_products_keyboard(call.from_user.id))


@menu.callback_query(Products.product_info, F.data == 'delete_product')
async def delete_product_callback(call: CallbackQuery, state: FSMContext):
    await state.set_state(Products.catalog)
    info = await state.get_data()
    product_id = info["product_id"]
    user_id = call.from_user.id
    await product_repo.delete_user_product(user_id, product_id)
    await call.message.answer("Товар удален!\n",
                                 reply_markup=menu_kb.main_menu)


@menu.callback_query(Products.product_info, F.data == 'update_info')
async def update_info_callback(call: CallbackQuery, state: FSMContext):
    info = await state.get_data()
    product_id = info["product_id"]
    user_id = call.from_user.id

    updatable_product = await product_repo.get_product_by_id(product_id)
    driver = webdriver.Chrome()
    driver.get(updatable_product.url)
    title, price = await get_title_and_price_info(updatable_product.url, driver)

    try:
        if updatable_product.price != price:
            await price_log_repo.add_price_log(updatable_product.id, price)
            await product_repo.change_product_price(updatable_product.id, price)
            await call.message.answer(f"Цена изменилась!\n "
                                         f"На {updatable_product.price - price} рублей.",
                                         reply_markup=menu_kb.product_info_menu)
        else:
            await call.message.answer("Цена не изменилась!",
                                         reply_markup=menu_kb.product_info_menu)
    except Exception as e:
        await call.message.answer(f"Ошибка при получении данных: {str(e)}",
                                     reply_markup=menu_kb.product_info_menu)
        driver.quit()
        return

    driver.quit()


@menu.callback_query(Products.product_info, F.data == 'price_log')
async def price_log_callback(call: CallbackQuery, state: FSMContext):
    info = await state.get_data()
    product_id = info["product_id"]
    logs = await price_log_repo.get_logs_by_product_id(product_id)
    text = ""

    for log in logs:
        formatted_time = log.timestamp.strftime("%Y.%m.%d %H:%M:%S")
        text += f"Время: {formatted_time}\t Цена: {log.price}\n\n"
    await call.message.answer(text, reply_markup=util_kb.back)


@menu.callback_query(F.data == "change_interval")
async def change_interval_callback(call: CallbackQuery, state: FSMContext):
    await state.set_state(Products.change_interval)
    await call.message.answer(f"Выберите новый интервал, с которым вам будут приходить оповещения о товарах",
                                 reply_markup=menu_kb.interval_values)


@menu.callback_query(Products.change_interval)
async def confirm_change_interval_callback(call: CallbackQuery, state: FSMContext):
    await state.clear()
    new_interval = int(call.data)
    user_id = call.from_user.id
    await check_interval_repo.edit_check_interval(user_id, new_interval)
    await call.message.answer(f"Интервал изменен!\n", reply_markup=menu_kb.main_menu)


async def get_title_and_price_info(url, driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    print("сайт загружен!")
    css_parser = CSSParser()
    parsed_url = urlparse(url)
    title_class, price_class = await css_parser.get_classes(parsed_url.netloc)

    print(title_class + " " + price_class)

    if 'ozon.ru' in parsed_url.netloc:
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "rb"))
        )
        button.click()

    title_element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, title_class))
    )
    print(title_element.text)
    title = title_element.text.strip()
    print(title)
    price = 0.0
    print(price)

    if 'lamoda.ru' in parsed_url.netloc:
        price_elements = driver.find_elements(By.CLASS_NAME, price_class)
        if len(price_elements) > 1:
            price = price_elements[1].text.strip()
        elif len(price_elements) == 1:
            price = price_elements[0].text.strip()
    else:
        try:
            print("Первая попытка запарсить!")
            price_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, price_class))
            )
            price = price_element.text.strip()
            print(price)
        except Exception as e:
            print("Не получилось в первый раз!")
            new_price_class = await css_parser.get_reserve_class(parsed_url.netloc)
            price_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, new_price_class))
            )
            price = price_element.text.strip()
            print(price)
    price = float(re.sub(r'[^\d.]', '', price))
    print(price)
    return title, price
