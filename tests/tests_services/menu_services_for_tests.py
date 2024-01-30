"""
Модуль с операциями взаимодействия с БД, которые касаются тестов для меню.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 31 января 2024
"""

from conftest import async_session_maker
from menu.menu_services import select_all_menus, select_specific_menu


async def get_all_menus_data() -> None:
    """
    Выборка всех меню из БД

    Returns:
        None
    """
    # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
    async with async_session_maker() as session:
        menus_data = await select_all_menus(session=session)

        try:
            # Т.к. в рамках теста запись одна, получаем ее из списка
            menus_data_json = menus_data[0].json()

            return [menus_data_json]
        except IndexError:
            return []


async def get_menu_data_from_db_without_counters() -> None:
    """
    Выборка определенного меню без счетчиков.

    Returns:
        None
    """
    # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
    async with async_session_maker() as session:
        # Получаем все меню.
        menus_data = await select_all_menus(session=session)
        # Т.к. оно одно, забираем первое и преобразуем в json.
        menu_data_json = menus_data[0].json()

        return menu_data_json


async def get_menu_data_from_db_with_counters() -> None:
    """
    Выборка определенного меню с счетчиками.

    Returns:
        None
    """
    # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
    async with async_session_maker() as session:
        # Т.к. menu в рамках теста одно, мы можем получить его id, для того чтобы тестирование БД и Response были
        # независимы
        menus_data = await select_all_menus(session=session)
        menus_data_json = menus_data[0].json()
        menu_id_in_db = menus_data_json["id"]

        # Здесь будет кортеж со списком вида [(<MENU OBJECT>, submenus_count, dishes_count)]
        menus_with_counts = await select_specific_menu(session=session, target_menu_id=menu_id_in_db)

        if menus_with_counts:
            menu = menus_with_counts[0][0]
            menu.submenus_count = menus_with_counts[0][1]
            menu.dishes_count = menus_with_counts[0][2]

            return menu.json()
