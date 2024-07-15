from database.models import User, Product, UserProduct, PriceLog
from database.app_db_context import async_session
from sqlalchemy import select, update, delete, desc

import datetime

from database.repositories import user as user_repo


async def add_price_log(product_id, price):
    async with async_session() as session:
        session.add(PriceLog(
            product_id=product_id,
            price=price,
            timestamp=datetime.datetime.now()
        ))
        await session.commit()


async def get_last_log_by_product_id(product_id):
    async with async_session() as session:
        result = await session.scalar(
            select(PriceLog)
            .where(PriceLog.product_id == product_id)
            .order_by(desc(PriceLog.timestamp))
            .limit(1)
        )
        return result


async def get_penultimate_log_by_product_id(product_id):
    async with async_session() as session:
        result = await session.scalar(
            select(PriceLog)
            .where(PriceLog.product_id == product_id)
            .order_by(desc(PriceLog.timestamp))
            .offset(1)
            .limit(1)
        )
        return result


async def get_logs_by_product_id(product_id):
    async with async_session() as session:
        result = await session.scalars(
            select(PriceLog)
            .where(PriceLog.product_id == product_id)
        )
        return result
