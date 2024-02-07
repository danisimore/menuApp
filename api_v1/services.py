"""
Бизнес логика, общая для приложений.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 06 февраля 2024
"""
from typing import Any

from database.database import get_async_session
from dish.models import Dish
from fastapi import Depends
from menu.models import Menu
from redis_tools.tools import RedisTools
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from submenu.models import Submenu
from utils import get_created_object_dict


async def insert_data(
        data_dict: dict[Any, Any],
        database_model: Menu | Submenu | Dish,
        session: AsyncSession = Depends(get_async_session)
) -> dict[Any, Any]:
    """
    Функция для внесения данных в БД.

    Args:
        data_dict: сформированный словарь на основе данных, полученных из запроса
        database_model: модель данных, для которой создается запись
        session: сессия подключения к БД.

    Returns: словарь, построенный на основе созданного объекта (новой записи в БД)

    """

    stmt = insert(database_model).values(data_dict).returning(database_model)

    result = await session.execute(stmt)

    created_object = result.scalars().all()[0]

    created_object_dict = get_created_object_dict(
        created_object=created_object)

    await session.commit()

    return created_object_dict


async def get_cache(key: str) -> list[dict[Any, Any]] | dict[Any, Any]:
    """
    Возвращает значение ключа из Redis

    :param key: ключ, по которому нужно получить значение
    :return:
    """

    redis = RedisTools()

    cache = await redis.get_pair(key=key)

    return cache


async def create_cache(key: str, value: list[Any] | dict[Any, Any]) -> None:
    """
    Создает пару ключ: значение в Redis

    :param key: ключ, для доступа к данным
    :param value: данные, которые будут хранится по этому ключу
    :return: None
    """
    redis = RedisTools()

    await redis.set_pair(key=key, value=value)


async def delete_cache(key: str) -> None:
    """
    Удаляет пару ключ: значение в Redis

    :param key: ключ, для доступа к данным
    :return: None
    """
    redis = RedisTools()

    await redis.invalidate_cache(key=key)


async def delete_all_cache() -> None:
    """
    Удаляет все данные

    :return: None
    """
    redis = RedisTools()

    await redis.invalidate_all_cache()
