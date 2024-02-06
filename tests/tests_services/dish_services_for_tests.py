"""
Модуль с операциями взаимодействия с БД, которые касаются тестов для блюд.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 31 января 2024
"""
from typing import Any

from conftest import async_session_maker
from database.database_services import (
    select_all_dishes,
    select_all_menus,
    select_all_submenus,
    select_specific_dish,
)
from dish.models import Dish


async def select_dishes() -> list[Dish]:
    """
    Выборка всех блюд из БД

    Returns:
        Если блюда найдены, то список с объектами блюд, если нет, то пустой список
    """
    # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
    async with async_session_maker() as session:
        try:
            # Т.к. menu в рамках теста одно, мы можем получить его id, для того чтобы тестирование БД и Response были
            # независимы
            menus_data = await select_all_menus(session=session)
            menus_data_json = await menus_data[0].json()
            menu_id_in_db = menus_data_json['id']

            # Т.к. menu в рамках теста одно, мы можем получить его id, для того чтобы тестирование БД и Response были
            # независимы
            submenus_data = await select_all_submenus(
                session=session, target_menu_id=menu_id_in_db
            )
            submenus_data_json = await submenus_data[0].json()
            submenu_id_in_db = submenus_data_json['id']

            dishes = await select_all_dishes(
                session=session,
                target_menu_id=menu_id_in_db,
                target_submenu_id=submenu_id_in_db,
            )
        except IndexError:
            return []

        return dishes


async def get_dish_by_index(index: int) -> list[dict[Any, Any]] | list[Any]:
    """
    Возвращает данные о блюде по указанному индексу из выборки всех блюд.

    Args:
        index: индекс блюда в выборке всех блюд

    Returns:
        Если блюдо существует, то список со словарем с данными о блюде, иначе пустой список
    """

    dishes = await select_dishes()

    try:
        dishes_json = await dishes[index].json()
        return [dishes_json]
    except IndexError:
        return []


async def get_specific_dish_data_from_db() -> Dish | dict[str, str]:
    """
    Выборка определенного блюда из БД.

    Returns:
        Если блюдо найдено, то объект блюда, иначе словарь с информацией о том, что блюдо не найдено
    """
    # Проверяем, чтобы данные, которые отдал сервер соответствовали данным в БД.
    async with async_session_maker() as session:
        # Т.к. menu в рамках теста одно, мы можем получить его id, для того чтобы тестирование БД и Response были
        # независимы
        menus_data = await select_all_menus(session=session)
        menus_data_json = await menus_data[0].json()
        menu_id_in_db = menus_data_json['id']

        # Т.к. menu в рамках теста одно, мы можем получить его id, для того чтобы тестирование БД и Response были
        # независимы
        submenus_data = await select_all_submenus(
            session=session, target_menu_id=menu_id_in_db
        )
        submenus_data_json = await submenus_data[0].json()
        submenu_id_in_db = submenus_data_json['id']

        dishes_data = await select_all_dishes(
            session=session,
            target_menu_id=menu_id_in_db,
            target_submenu_id=submenu_id_in_db,
        )

        try:
            dishes_data_json = await dishes_data[0].json()
            dish_id_in_db = dishes_data_json['id']

            dish = await select_specific_dish(
                session=session,
                target_menu_id=menu_id_in_db,
                target_submenu_id=submenu_id_in_db,
                target_dish_id=dish_id_in_db,
            )

            return dish
        except IndexError:
            return {'detail': 'dish not found'}
