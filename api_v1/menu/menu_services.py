"""
Бизнес логика, специфичная для модуля.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 22 января 2024
"""

from sqlalchemy import select, update, cast, Boolean, delete

from sqlalchemy import Result
from sqlalchemy.orm import selectinload

from menu.models import Menu


async def select_all_menus(session):
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


async def select_specific_menu(target_menu_id: str, submenu, session):
    """
    Функция для выборки меню, по указанному id.

    Args:
        target_menu_id: идентификатор меню, полученный из запроса
        submenu: класс модели данных Submenu. Нужен для включения в запрос привязанных подменю и дальнейшего их подсчета
        session: сессия подключения к БД.

    Returns: объект найденного меню.

    """

    stmt = (
        select(Menu)
        .where(Menu.id == target_menu_id)
        .options(selectinload(Menu.submenus).options(selectinload(submenu.dishes)))
    )
    result = await session.execute(stmt)

    menu = result.scalar_one_or_none()

    return menu


async def update_menu(update_menu_data, target_menu_id: str, session):
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


async def delete_menu(target_menu_id: str, session) -> None:
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
