"""
Бизнес логика, специфичная для модуля.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 22 января 2024
"""

from fastapi import Depends

from sqlalchemy import select, update, cast, Boolean, delete, func, distinct

from sqlalchemy import Result
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_async_session

from menu.models import Menu
from menu.schemas import MenuUpdate

from dish.models import Dish
from submenu.models import Submenu


async def select_all_menus(session: AsyncSession = Depends(get_async_session)) -> list[Menu]:
    """
    Функция для выборки всех меню из таблицы menus.

    Args:
        session: сессия подключения к БД.

    Returns: объект найденных меню.

    """

    stmt = select(Menu)
    result: Result = await session.execute(stmt)

    menus = result.scalars().all()

    return menus


async def select_specific_menu(
        target_menu_id: str,
        session: AsyncSession = Depends(get_async_session)
) -> list[tuple[Menu, int, int]]:
    """
    Функция для выборки меню, по указанному id.

    Args:
        target_menu_id: идентификатор меню, полученный из запроса
        session: сессия подключения к БД.

    Returns: объект найденного меню.

    """

    stmt = (
        select(
            Menu,
            func.count(distinct(Submenu.id)).label("submenus_count"),
            func.count(distinct(Dish.id)).label("dishes_count"),
        )
        .outerjoin(Submenu, Submenu.menu_id == Menu.id)
        .outerjoin(Dish, Dish.submenu_id == Submenu.id)
        .group_by(Menu.id)
    ).where(Menu.id == target_menu_id)

    result = await session.execute(stmt)

    menus_with_counts = result.all()

    return menus_with_counts


async def update_menu(
        update_menu_data: MenuUpdate,
        target_menu_id: str,
        session: AsyncSession = Depends(get_async_session)
) -> Menu:
    """
    Функция для обновления записи в БД по заданному id меню.

    Args:
        update_menu_data: данные, на которые будут заменены текущие
        target_menu_id: id записи, которую необходимо обновить
        session: сессия подключения к БД.

    Returns: обновленная запись.

    """

    # Генерируем SQL код для того, чтобы обновить данные записи и вернуть их.
    stmt = (
        update(Menu)
        .values(**update_menu_data.model_dump())
        .where(cast(Menu.id == target_menu_id, Boolean))
        .returning(Menu)
    )

    # Исполняем SQL код.
    result = await session.execute(stmt)

    # Получаем объект созданной записи.
    updated_menu = result.scalars().all()[0]

    await session.commit()

    return updated_menu


async def delete_menu(
        target_menu_id: str,
        session: AsyncSession = Depends(get_async_session)
) -> None:
    """
    Функция для удаления записи из БД.

    Args:
        target_menu_id: id записи, которую необходимо удалить
        session: сессия подключения к БД.

    Returns: None

    """
    stmt = delete(Menu).where(cast(Menu.id == target_menu_id, Boolean))

    await session.execute(stmt)

    await session.commit()
