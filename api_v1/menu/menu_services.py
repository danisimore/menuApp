"""
Бизнес логика, специфичная для модуля.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 06 февраля 2024
"""

from database.database import get_async_session
from dish.models import Dish
from fastapi import Depends
from menu.models import Menu
from menu.schemas import MenuUpdate
from sqlalchemy import Boolean, Result, cast, delete, distinct, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
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
            func.count(distinct(Submenu.id)).label('submenus_count'),
            func.count(distinct(Dish.id)).label('dishes_count'),
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


async def parse_menu_data(menu_data: list[tuple[Menu, int, int]]) -> Menu | None:
    """
    Парсит полученный список с кортежем, в котором хранится Объект, счетчик подменю и блюд

    :param menu_data: список с кортежем, в котором хранится Объект, счетчик подменю и блюд
    :return: если в ходе выборки нашлось меню, то меню с добавленными атрибутами submenus_count и dishes_count
    """
    if menu_data:
        menu = menu_data[0][0]
        menu.submenus_count = menu_data[0][1]
        menu.dishes_count = menu_data[0][2]

        return menu

    return None
