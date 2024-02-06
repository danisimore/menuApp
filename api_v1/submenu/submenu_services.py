"""
Бизнес логика, специфичная для модуля.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 06 февраля 2024
"""


from database.database import get_async_session
from database.database_services import get_dishes_for_submenu
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from submenu.models import Submenu

from .submenu_utils import format_dishes


async def prepare_submenu_to_response(submenu: Submenu, session: AsyncSession = Depends(get_async_session)):
    """
    Добавляет dishes_count к подменю и преобразует dishes из объектов в json

    :param submenu: объект подменю
    :param session: сессия подключения к БД

    :return: json объект подменю
    """

    # Получаем блюда для этого подменю
    submenu_dishes = await get_dishes_for_submenu(submenu.id, session)

    # Преобразуем объект меню в json
    submenu_json = await submenu.json()
    # Считаем кол-во блюд для этого меню
    submenu_json['dishes_count'] = len(submenu_dishes)
    # Преобразуем найденные блюда к json.
    submenu_json['dishes'] = await format_dishes(submenu_dishes)

    return submenu_json
