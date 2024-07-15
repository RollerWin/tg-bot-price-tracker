from database.models import User
from database.app_db_context import async_session
from sqlalchemy import select, update, delete


async def add_user(tg_id, username):
    async with async_session() as session:
        session.add(User(tg_id=tg_id, username=username))
        await session.commit()


async def is_user_exists(tg_id):
    async with async_session() as session:
        result = await session.scalar(select(User).where(User.tg_id == tg_id))

        if result:
            return True
        else:
            return False


async def edit_username(tg_id, username):
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.tg_id == tg_id)
            .values(username=username)
        )
        await session.commit()


async def get_user_id(tg_id):
    async with async_session() as session:
        user_id = await session.scalar(
            select(User.id)
            .where(User.tg_id == tg_id)
        )
        return user_id


async def get_username(tg_id):
    async with async_session() as session:
        username = await session.scalar(
            select(User.username)
            .where(User.tg_id == tg_id)
        )
        return username


async def get_user_info(tg_id):
    async with async_session() as session:
        user_info = await session.scalar(
            select(User)
            .where(User.tg_id == tg_id)
        )
        return user_info


async def delete_user(tg_id):
    async with async_session() as session:
        await session.execute(
            delete(User)
            .where(User.tg_id == tg_id)
        )
        await session.commit()


async def get_tg_id_by_user_id(user_id):
    async with async_session() as session:
        tg_id = await session.scalar(
            select(User.tg_id)
            .where(User.id == user_id)
        )
        return tg_id