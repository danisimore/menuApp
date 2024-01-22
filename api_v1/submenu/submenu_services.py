"""
Бизнес логика, специфичная для модуля.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 22 января 2024
"""
from fastapi import Depends
from sqlalchemy import select, and_, update, delete

from sqlalchemy import cast, Boolean, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.database import get_async_session
from submenu.models import Submenu
from submenu.schemas import UpdateSubmenu


async def select_all_submenus(
    target_menu_id: str, session: AsyncSession = Depends(get_async_session)
) -> list:
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
) -> list:
    """
    Функция для выборки определнного подменю.

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

    return submenu


async def update_submenu(
    target_menu_id: str,
    target_submenu_id: str,
    update_submenu_data: UpdateSubmenu,
    session: AsyncSession = Depends(get_async_session),
) -> list:
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


async def delete_submenu(target_menu_id: str, target_submenu_id, session) -> None:
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
