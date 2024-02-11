"""
Модуль с операциями взаимодействия с БД, которые касаются тестов для меню.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 08 февраля 2024 | Добавлена выборка всех меню со всеми связанными подменю и со всеми связанными блюдами из БД
"""
from typing import Any

from conftest import async_session_maker
from database.database_services import (
    select_all_menus,
    select_all_menus_detail,
    select_specific_menu,
)
from menu.menu_utils import format_detailed_menus


async def get_all_menus_detail_data() -> list[dict[Any, Any]]:
    """
    Выборка всех меню из БД со связанными подменю и блюдами

    :return: список со всеми меню с отображением привязанных подменю и блюд
    """

    async with async_session_maker() as session:
        menus_data = await select_all_menus_detail(session=session)
        menus_json = await format_detailed_menus(menus=menus_data, session=session)

    return menus_json


async def get_all_menus_data() -> list[dict[Any, Any]] | list[Any] | None:
    """
    Выборка всех меню из БД

    Returns:
        Если меню найдены, то список с меню, если нет, то пустой список
    """
    async with async_session_maker() as session:
        menus_data = await select_all_menus(session=session)

        if not len(menus_data):
            return []

        menus_data_json = await menus_data[0].json()

        return [menus_data_json]


async def get_menu_data_from_db_without_counters() -> dict[Any, Any]:
    """
    Выборка определенного меню без счетчиков.

    Returns:
        Объект в формате словаря
    """
    async with async_session_maker() as session:
        # Получаем все меню.
        menus_data = await select_all_menus(session=session)
        menu_data_json = await menus_data[0].json()

        return menu_data_json


async def get_menu_data_from_db_with_counters() -> dict[Any, Any] | None:
    """
    Выборка определенного меню со счетчиками.

    Returns:
        Если меню найдено, то словарь с данными о меню, иначе None
    """
    # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
    async with async_session_maker() as session:
        menus_data = await select_all_menus(session=session)
        menus_data_json = await menus_data[0].json()
        menu_id_in_db = menus_data_json['id']

        menus_with_counts = await select_specific_menu(
            session=session, target_menu_id=menu_id_in_db
        )

        if menus_with_counts:
            menu = menus_with_counts[0][0]
            menu.submenus_count = menus_with_counts[0][1]
            menu.dishes_count = menus_with_counts[0][2]

            menu_json = await menu.json()

            return menu_json

    return None
