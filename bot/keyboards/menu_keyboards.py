from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.repositories import product as product_repo

interval_values = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Каждая 1 минута", callback_data="1")],
    [InlineKeyboardButton(text="Каждые 30 минут", callback_data="10")],
    [InlineKeyboardButton(text="Каждый 1 час", callback_data="24")]
])

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Новый товар", callback_data="new_product")],
    [InlineKeyboardButton(text="Мои товары", callback_data="catalog")],
    [InlineKeyboardButton(text="Изменить частоту обновления", callback_data="change_interval")]
])

product_info_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Обновить данные", callback_data="update_info")],
    [InlineKeyboardButton(text="Перестать отслеживать", callback_data="delete_product")],
    [InlineKeyboardButton(text="История цены", callback_data="price_log")],
    [InlineKeyboardButton(text="Назад", callback_data="back")]
])


async def get_products_keyboard(tg_id):
    products = await product_repo.get_user_products(tg_id)
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Назад", callback_data="back"))
    for product in products:
        keyboard.add(InlineKeyboardButton(text=product.name, callback_data=f"product_{product.id}"))
    return keyboard.adjust(1).as_markup()
