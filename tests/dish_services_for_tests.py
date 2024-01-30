"""
Модуль с операциями взаимодействия с БД, которые касаются тестов для блюд.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 31 января 2024
"""

from conftest import async_session_maker
from dish.dish_services import select_all_dishes, select_specific_dish
from menu.menu_services import select_all_menus
from submenu.submenu_services import select_all_submenus


async def select_dishes() -> None:
    """
    Выборка всех блюд из БД

    Returns:
        None
    """
    # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
    async with async_session_maker() as session:
        try:
            # Т.к. menu в рамках теста одно, мы можем получить его id, для того чтобы тестирование БД и Response были
            # независимы
            menus_data = await select_all_menus(session=session)
            menus_data_json = menus_data[0].json()
            menu_id_in_db = menus_data_json["id"]

            # Т.к. menu в рамках теста одно, мы можем получить его id, для того чтобы тестирование БД и Response были
            # независимы
            submenus_data = await select_all_submenus(session=session, target_menu_id=menu_id_in_db)
            submenus_data_json = submenus_data[0].json()
            submenu_id_in_db = submenus_data_json["id"]

            dishes = await select_all_dishes(session=session, target_menu_id=menu_id_in_db,
                                             target_submenu_id=submenu_id_in_db)
        except IndexError:
            return []

        return dishes


async def get_first_dish_data_from_db() -> None:
    """
    Выборка первого блюда из БД.

    Returns:
        None
    """

    dishes = await select_dishes()

    try:
        dishes_json = dishes[0].json()
        return [dishes_json]
    except IndexError:
        return []


async def get_second_dish_data_from_db() -> None:
    """
    Выборка второго блюда из БД.

    Returns:
        None
    """

    dishes = await select_dishes()
    try:
        dishes_json = dishes[1].json()
        return [dishes_json]
    except IndexError:
        return []


async def get_specific_dish_data_from_db() -> None:
    """
    Выборка определенного блюда из БД.

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

        # Т.к. menu в рамках теста одно, мы можем получить его id, для того чтобы тестирование БД и Response были
        # независимы
        submenus_data = await select_all_submenus(session=session, target_menu_id=menu_id_in_db)
        submenus_data_json = submenus_data[0].json()
        submenu_id_in_db = submenus_data_json["id"]

        dishes_data = await select_all_dishes(session=session, target_menu_id=menu_id_in_db,
                                              target_submenu_id=submenu_id_in_db)

        try:
            dishes_data_json = dishes_data[0].json()
            dish_id_in_db = dishes_data_json["id"]

            dish = await select_specific_dish(
                session=session,
                target_menu_id=menu_id_in_db,
                target_submenu_id=submenu_id_in_db,
                target_dish_id=dish_id_in_db
            )

            return dish
        except IndexError:
            return {'detail': 'dish not found'}
