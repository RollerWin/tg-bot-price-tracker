from database.models import User, Product, UserProduct, CheckInterval
from database.app_db_context import async_session
from sqlalchemy import select, update, delete

import datetime

from database.repositories import user as user_repo


async def add_check_interval(tg_id, interval):
    async with async_session() as session:
        # user_id = await user_repo.get_user_id(tg_id)
        session.add(CheckInterval(
            user_id=tg_id,
            interval=interval
        ))
        await session.commit()


async def edit_check_interval(tg_id, interval):
    async with async_session() as session:
        # user_id = await user_repo.get_user_id(tg_id)
        await session.execute(
            update(CheckInterval)
            .where(CheckInterval.user_id == tg_id)
            .values(interval=interval)
        )
        await session.commit()


async def get_users_by_interval(interval):
    async with async_session() as session:
        result = await session.scalars(
            select(CheckInterval.user_id)
            .where(CheckInterval.interval == interval)
        )
        return result
