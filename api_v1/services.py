"""
Бизнес логика, общая для приложений.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 22 января 2024
"""

from database.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from sqlalchemy import insert
from utils import get_created_object_dict
from menu.models import Menu
from submenu.models import Submenu
from dish.models import Dish


async def insert_data(
        data_dict: dict,
        database_model: Menu | Submenu | Dish,
        session: AsyncSession = Depends(get_async_session)
) -> dict:
    """
    Функция для внесения данных в БД.

    Args:
        data_dict: сформированный словарь на основе данных, полученных из запроса
        database_model: модель данных, для которой создается запись
        session: сессия подключения к БД.

    Returns: словарь, построенный на основе созданного объекта (новой записи в БД)

    """

    # Формируем SQL код.
    stmt = insert(database_model).values(data_dict).returning(database_model)

    # Исполняем его.
    result = await session.execute(stmt)
    # Получаем созданный объект.
    created_object = result.scalars().all()[0]
    # Формируем словарь из данных созданного объекта, чтобы вернуть его
    # пользователю в виде JSON
    created_object_dict = get_created_object_dict(
        created_object=created_object)

    await session.commit()

    return created_object_dict
