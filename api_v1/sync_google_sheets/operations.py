"""
Модуль реализующий операции для синхронизации гугл таблицы с БД

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru

Дата: 11 февраля 2024
"""

from database.database import get_async_session
from database.database_services import delete_menu
from dish.models import Dish
from menu.models import Menu
from services import create_cache, delete_all_cache, insert_data
from submenu.models import Submenu


async def clear_tables() -> None:
    """
    Удаляет все записи из таблиц.

    :return: None
    """
    async for session in get_async_session():
        await delete_menu(session=session)
        await delete_all_cache()


async def create_menu_using_data_from_sheets(menu_data_from_table: list[str]) -> str | None:
    """
    Создает меню используя данные из гугл таблицы

    :param menu_data_from_table: данные о меню, полученные из sheets, которое нужно создать
    :return: str - uuid созданного меню
    """
    cntr = 0
    menu_data = {}

    for data in menu_data_from_table:
        if cntr == 1:
            menu_data['title'] = data
        elif cntr == 2:
            menu_data['description'] = data
            async for session in get_async_session():
                created_menu_dict = await insert_data(
                    data_dict=menu_data,
                    database_model=Menu,
                    session=session
                )

                target_menu_id = created_menu_dict['id']

                return target_menu_id

        cntr += 1

    return None


async def create_submenu_using_data_from_sheets(submenu_data_from_table: list[str], target_menu_id: str) -> str | None:
    """
    Создает подменю используя данные из гугл таблицы.

    :param submenu_data_from_table: данные о подменю, полученные из sheets, которое нужно создать.
    :param target_menu_id: uuid созданного ранее меню, для которого подменю создается
    :return: str - uuid созданного подменю
    """

    cntr = 0
    submenu_data = {}
    for data in submenu_data_from_table:
        if cntr == 2:
            submenu_data['title'] = data
        elif cntr == 3:
            submenu_data['description'] = data
            submenu_data['menu_id'] = target_menu_id
            async for session in get_async_session():
                created_submenu_dict = await insert_data(
                    data_dict=submenu_data,
                    database_model=Submenu,
                    session=session
                )
                target_submenu_id = created_submenu_dict['id']

                return target_submenu_id

        cntr += 1

    return None


async def create_dish_using_data_from_sheets(dish_data_from_table, target_submenu_id) -> None:
    """
    Создает блюдо используя данные из гугл таблицы

    :param dish_data_from_table: данные о блюде, полученные из sheets, которое нужно создать.
    :param target_submenu_id: uuid созданного ранее подменю, для которого блюдо создается
    :return: None
    """
    cntr = 0
    dish_data = {}

    for data in dish_data_from_table:
        if cntr == 3:
            dish_data['title'] = data
        elif cntr == 4:
            dish_data['description'] = data
        elif cntr == 5:
            formatted_price = data.replace(',', '.')
            dish_data['price'] = formatted_price
            dish_data['submenu_id'] = target_submenu_id

            async for session in get_async_session():
                created_dish_dict = await insert_data(
                    data_dict=dish_data,
                    database_model=Dish,
                    session=session
                )
                target_dish_id = created_dish_dict['id']
        elif cntr == 6:
            discount_perc = data
            discount_cache_key = 'discount_' + target_dish_id
            await create_cache(key=discount_cache_key, value=discount_perc)

        cntr += 1
