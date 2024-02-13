"""
Бизнес логика, общая для приложений.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 10 февраля 2024 | Добавлена функция для инвалидации всего кэша
"""
from typing import Any

from database.database import get_async_session
from database.database_services import get_dishes_for_submenu
from fastapi import Depends
from redis_tools.tools import RedisTools
from sqlalchemy.ext.asyncio import AsyncSession
from submenu.models import Submenu


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

    await delete_cache_by_key(key='table_cache')

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
