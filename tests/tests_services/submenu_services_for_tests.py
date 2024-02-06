"""
Модуль с операциями взаимодействия с БД, которые касаются тестов для подменю.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 31 января 2024
"""

from conftest import async_session_maker
from menu.menu_services import select_all_menus
from submenu.models import Submenu
from submenu.submenu_services import (
    get_dishes_for_submenu,
    select_all_submenus,
    select_specific_submenu,
)


async def get_submenus_data_from_db() -> list[dict] | list:
    """
    Выборка всех подменю из БД

    Returns:
        Если подменю найдены, то список с меню, если нет, то пустой список
    """
    # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
    async with async_session_maker() as session:
        # Т.к. menu в рамках теста одно, мы можем получить его id, для того чтобы тестирование БД и Response были
        # независимы
        menus_data = await select_all_menus(session=session)
        menus_data_json = await menus_data[0].json()
        menu_id_in_db = menus_data_json['id']

        submenus = await select_all_submenus(
            session=session, target_menu_id=menu_id_in_db
        )

        try:
            submenus_json = await submenus[0].json()

            submenu_id = submenus_json['id']
            submenu_dishes = await get_dishes_for_submenu(target_submenu_id=submenu_id, session=session)

            submenus_json['dishes'] = submenu_dishes

            return [submenus_json]
        except IndexError:
            return []


async def get_specific_submenu_data_from_db() -> Submenu | dict:
    """
    Выборка определенного подменю из БД

    Returns:
        Если submenu найдено, то объект Submenu, иначе информацию о том, что оно не найдено
    """

    # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
    async with async_session_maker() as session:
        # Т.к. menu в рамках теста одно, мы можем получить его id, для того чтобы тестирование БД и Response были
        # независимы
        menus_data = await select_all_menus(session=session)
        menus_data_json = await menus_data[0].json()
        menu_id_in_db = menus_data_json['id']

        # Т.к. submenu в рамках теста одно, мы можем получить его id, для того чтобы тестирование БД и Response были
        # независимы
        submenus_data = await select_all_submenus(
            session=session, target_menu_id=menu_id_in_db
        )
        try:
            submenus_data_json = await submenus_data[0].json()
            submenu_id_in_db = submenus_data_json['id']

            submenu = await select_specific_submenu(
                session=session,
                target_menu_id=menu_id_in_db,
                target_submenu_id=submenu_id_in_db,
            )

            dishes_for_submenu = await get_dishes_for_submenu(
                session=session, target_submenu_id=submenu_id_in_db
            )

            submenu.dishes_count = len(dishes_for_submenu)
            submenu.dishes = dishes_for_submenu

            return submenu
        except IndexError:
            return {'detail': 'submenu not found'}
