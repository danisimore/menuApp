"""
Бизнес логика, общая для приложений.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 08 февраля 2024 | Удалена неиспользуемая функция
"""
from typing import Any

from database.database import get_async_session
from database.database_services import get_dishes_for_submenu
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
    redis = RedisTools()
    await redis.invalidate_all_cache()


async def delete_cache_by_key(key: str) -> None:
    """
    Удаляет данные по ключу

    :param key: ключ, по которому нужно удалить данные
    :return: None
    """

    redis = RedisTools()

    await redis.invalidate_cache(key=key)


async def delete_linked_menu_cache(
        submenus_for_menu: list[Submenu],
        target_menu_id: str,
        session: AsyncSession = Depends(get_async_session)
) -> None:
    """
    Удаляет данные из кэша связанные с меню

    :param submenus_for_menu: подменю связанные с меню
    :param target_menu_id: id меню
    :param session: сессия подключения к БД
    :return: None
    """
    submenus_cache_key = target_menu_id + '_submenus'
    await delete_cache_by_key(key=submenus_cache_key)

    for submenu in submenus_for_menu:
        dishes_cache_key = target_menu_id + '_' + str(submenu.id) + '_dishes'
        await delete_cache_by_key(dishes_cache_key)

        await delete_linked_submenu_cache(
            target_submenu_id=str(submenu.id),
            target_menu_id=target_menu_id,
            session=session
        )

        await delete_cache_by_key(str(submenu.id))


async def delete_linked_submenu_cache(
        target_submenu_id: str,
        target_menu_id: str,
        session: AsyncSession = Depends(get_async_session)
) -> None:
    """
    Удаляет данные из кэша связанные с подменю

    :param target_submenu_id: id подменю
    :param target_menu_id: id связанного с ним меню
    :param session: сессия подключения к БД.
    :return: None
    """
    dishes = await get_dishes_for_submenu(target_submenu_id=target_submenu_id, session=session)

    dishes_cache_key = target_menu_id + '_' + target_submenu_id + '_dishes'
    await delete_cache_by_key(dishes_cache_key)

    for dish in dishes:
        specific_dish_cache_key = target_menu_id + '_' + target_submenu_id + '_' + str(dish.id)
        await delete_cache_by_key(specific_dish_cache_key)
