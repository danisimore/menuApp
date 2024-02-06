"""
Бизнес логика, специфичная для модуля.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 06 февраля 2024
"""
from typing import Any

from database.database import get_async_session
from database.database_services import select_submenus_for_menu
from dish.models import Dish
from fastapi import Depends
from sqlalchemy import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession
from submenu.models import Submenu

from .dish_utils import format_decimal


async def is_submenu_in_target_menu(
        submenu: type[Submenu],
        target_menu_id: str,
        target_submenu_id: str,
        session: AsyncSession = Depends(get_async_session),
) -> bool:
    """
    Функция для проверки соответствия связи между меню и подменю.

    Args:
        submenu: класс модели БД Submenu;
        target_menu_id: идентификатор меню, к которому должно быть привязано подменю
        session: сессия подключения к БД;
        target_submenu_id: идентификатор подменю, к которому должно быть привязано блюдо

    Returns: bool. True, если к указанному menu привязано указанное submenu, иначе False

    """

    submenus_linked_to_target_menu_id = await select_submenus_for_menu(
        submenu=submenu,
        target_menu_id=target_menu_id,
        session=session
    )

    # Если к меню привязаны подменю
    if submenus_linked_to_target_menu_id:
        # Итерируемся по этим подменю
        for submenu in submenus_linked_to_target_menu_id:
            # Если переданный в запросе идентификатор подменю, совпадает с идентификатором, привязанным к меню
            if str(submenu.id) == target_submenu_id:
                # Возвращаем True
                return True

    return False


async def try_get_dish(result: ChunkedIteratorResult) -> Dish | bool:
    """
    Функция для получения блюда из выборки

    :param result: результат выборки
    :return: Если блюдо найдено, то объект блюд, иначе False
    """

    try:
        dish = result.scalars().all()[0]
        return dish
    except IndexError:
        return False


async def generate_dish_dict(dish: Dish) -> dict[Any, Any]:
    """
    Формирует словарь на основе данных объекта блюда из БД

    :param dish: объект Dish
    :return: словарь с данными о блюде
    """
    # Формируем словарь, чтобы корректно отобразить цену (2 знака после запятой).
    dish_dict = {
        'id': str(dish.id),
        'title': dish.title,
        'description': dish.description,
        'price': format_decimal(dish.price),
        'submenu_id': str(dish.submenu_id),
    }

    return dish_dict
