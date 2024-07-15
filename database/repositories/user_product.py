from database.models import User, Product, UserProduct
from database.app_db_context import async_session
from sqlalchemy import select, update, delete

from database.repositories import user as user_repo, product as product_repo


async def add_product_to_user_relation(user_id, product_id):
    async with async_session() as session:
        session.add(UserProduct(user_id=user_id, product_id=product_id))
        await session.commit()


async def is_relation_exist(user_id, product_id):
    async with async_session() as session:
        result = await session.scalar(select(UserProduct)
                                      .where(UserProduct.user_id == user_id,
                                             UserProduct.product_id == product_id)
                                      )
        return result
