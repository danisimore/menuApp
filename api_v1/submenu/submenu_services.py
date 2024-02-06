"""
Бизнес логика, специфичная для модуля.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 06 февраля 2024
"""

from database.database import get_async_session
from dish.models import Dish
from fastapi import Depends
from sqlalchemy import Boolean, Result, and_, cast, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from submenu.models import Submenu
from submenu.schemas import UpdateSubmenu
from .submenu_utils import format_dishes


async def get_dishes_for_submenu(
    target_submenu_id: str, session: AsyncSession = Depends(get_async_session)
) -> list[Dish]:
    stmt = select(Dish).where(Dish.submenu_id == target_submenu_id)

    result: Result = await session.execute(stmt)

    dishes = result.scalars().all()

    return dishes


async def select_all_submenus(
    target_menu_id: str, session: AsyncSession = Depends(get_async_session)
) -> list[Submenu]:
    """
    Функция для выборки всех подменю привязанных к указанному меню.

    Args:
        target_menu_id: идентификатор меню, для которого идет поиск подменю
        session: сессия подключения к БД.

    Returns: объект найденных подменю

    """

    stmt = select(Submenu).where(cast(Submenu.menu_id == target_menu_id, Boolean))

    result: Result = await session.execute(stmt)

    submenus = result.scalars().all()

    return submenus


async def select_specific_submenu(
    target_menu_id: str,
    target_submenu_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> Submenu | None:
    """
    Функция для выборки определенного подменю.

    Args:
        target_menu_id: идентификатор меню, с которым должно быть связанно искомое подменю
        target_submenu_id: идентификатор искомого подменю
        session: сессия подключения к БД.

    Returns: Список с найденным подменю, либо пустой список

    """

    stmt = (
        select(Submenu)
        .where(and_(Submenu.menu_id == target_menu_id, Submenu.id == target_submenu_id))
        .options(selectinload(Submenu.dishes))
    )

    result: Result = await session.execute(stmt)

    submenu = result.scalars().all()

    try:
        return submenu[0]
    except IndexError:
        return None


async def update_submenu(
    target_menu_id: str,
    target_submenu_id: str,
    update_submenu_data: UpdateSubmenu,
    session: AsyncSession = Depends(get_async_session),
) -> list[Submenu]:
    """
    Функция для обновления записи в таблице submenus.

    Args:
        target_menu_id: идентификатор меню, с которым должно быть связанно обновляемое подменю.
        target_submenu_id: идентификатор обновляемого подменю.
        update_submenu_data: данные, на которые нужно обновить текущие.
        session: сессия подключения к БД.

    Returns: Объект обновленного подменю.

    """

    stmt = (
        update(Submenu)
        .where(and_(Submenu.menu_id == target_menu_id, Submenu.id == target_submenu_id))
        .values(**update_submenu_data.model_dump())
        .returning(Submenu)
    )

    result = await session.execute(stmt)

    updated_submenu = result.scalars().all()

    await session.commit()

    return updated_submenu


async def delete_submenu(
        target_menu_id: str,
        target_submenu_id: str,
        session: AsyncSession = Depends(get_async_session),
) -> None:
    """
    Функция для удаления подменю по указанным данным.

    Args:
        target_menu_id: идентификатор меню, с которым должно быть связанно удаляемое подменю
        target_submenu_id: идентификатор удаляемого подменю
        session: сессия подключения к БД.

    Returns: None

    """

    stmt = delete(Submenu).where(
        and_(Submenu.menu_id == target_menu_id, Submenu.id == target_submenu_id)
    )

    await session.execute(stmt)

    await session.commit()


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
