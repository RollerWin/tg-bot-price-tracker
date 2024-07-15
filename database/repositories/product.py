from database.models import Product, UserProduct
from database.app_db_context import async_session
from sqlalchemy import select, update, delete

from database.repositories import user as user_repo


async def add_product(name, price, url):
    async with async_session() as session:
        session.add(Product(name=name, is_available=True, price=price, url=url))
        await session.commit()


async def delete_user_product(tg_id, product_id):
    async with async_session() as session:
        user_id = await user_repo.get_user_id(tg_id)
        await session.execute(
            delete(UserProduct)
            .where(UserProduct.user_id == user_id,
                   UserProduct.product_id == product_id)
        )
        await session.commit()


async def get_all_products():
    async with async_session() as session:
        products = await session.scalars(select(Product))
        return products


async def is_product_already_exist(url):
    async with async_session() as session:
        product = await session.scalar(select(Product).where(Product.url == url))
        return product


async def get_user_products(tg_id):
    async with async_session() as session:
        user_id = await user_repo.get_user_id(tg_id)
        user_products = await session.scalars(select(Product).join(UserProduct).where(UserProduct.user_id == user_id))
        return user_products


async def get_product_by_id(product_id):
    async with async_session() as session:
        product = await session.scalar(select(Product).where(Product.id == product_id))
        return product


async def get_product_id_by_name(name):
    async with async_session() as session:
        product = await session.scalar(select(Product).where(Product.name == name))
        return product


async def change_product_price(product_id, price):
    async with async_session() as session:
        await session.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(price=price)
        )
        await session.commit()
