"""
Бизнес логика, специфичная для модуля.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru

Дата: 10 февраля 2024 | Добавлена функция форматирования списка подменю. Реализовано применение скидки для блюд
в подменю
"""
from typing import Any

from database.database import get_async_session
from database.database_services import get_dishes_for_submenu
from dish.dish_utils import apply_discount
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from submenu.models import Submenu
from submenu.submenu_utils import format_dishes


async def prepare_submenus_to_response(
        submenus: list[Submenu],
        session: AsyncSession = Depends(get_async_session)
) -> list[dict[Any, Any]]:
    """
    Добавляет dishes_count ко всем подменю переданным в списке и преобразует dishes из объектов в json,
    добавляет скидку к цене блюда, если таковая имеется

    :param submenus: Список объектов подменю, которые необходимо отформатировать
    :param session: сессия подключения к БД
    :return: Список с данными об объектах подменю в формате JSON
    """

    submenus_list = []
    for submenu in submenus:
        prepared_submenu = await prepare_submenu_to_response(submenu=submenu, session=session)
        submenus_list.append(prepared_submenu)

    return submenus_list


async def prepare_submenu_to_response(submenu: Submenu, session: AsyncSession = Depends(get_async_session)):
    """
    Добавляет dishes_count к определенному подменю и преобразует dishes из объектов в json, добавляет скидку к цене
    блюда, если таковая имеется

    :param submenu: объект подменю
    :param session: сессия подключения к БД

    :return: json объект подменю
    """

    submenu_dishes = await get_dishes_for_submenu(submenu.id, session)

    submenu_json = await submenu.json()
    submenu_json['dishes_count'] = len(submenu_dishes)

    submenu_json['dishes'] = await format_dishes(submenu_dishes)
    dishes_with_discounts = await apply_discount(submenu_json['dishes'])

    submenu_json['dishes'] = dishes_with_discounts

    return submenu_json
