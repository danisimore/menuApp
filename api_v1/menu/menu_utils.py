"""
Функции специфичные для модуля не относящиеся к бизнес-логике.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 11 февраля 2024
"""

from typing import Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_async_session
from submenu.submenu_services import prepare_submenus_to_response
from menu.models import Menu


async def format_detailed_menus(
        menus: list[Menu],
        session: AsyncSession = Depends(get_async_session)
) -> list[dict[Any, Any]]:
    """
    Форматирует объекты меню из списка выборки и связанные с ним подменю и блюда в json

    :param menus: список меню
    :param session: сессия подключения к БД
    :return: список со всеми отформатированными меню с отображением привязанных подменю и блюд
    """
    menus_json = []

    for menu in menus:
        menus_json.append(await menu.json_detail())

    for menu in menus_json:
        formatted_submenus = await prepare_submenus_to_response(menu['submenus'], session=session)
        menu['submenus'] = formatted_submenus

    return menus_json
