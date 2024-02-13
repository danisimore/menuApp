"""
Cлой для работы с БД.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 08 февраля 2024 | Реализация и вывода всех меню со всеми связанными подменю и со всеми связанными блюдами.
"""
from typing import Any

from database.database import get_async_session
from dish.models import Dish
from dish.schemas import UpdateDish
from fastapi import Depends
from menu.models import Menu
from menu.schemas import MenuUpdate
from sqlalchemy import (
    Boolean,
    Result,
    and_,
    cast,
    delete,
    distinct,
    func,
    insert,
    select,
    update,
)
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from submenu.models import Submenu
from submenu.schemas import UpdateSubmenu
from utils import get_created_object_dict


async def insert_data(
        data_dict: dict[Any, Any],
        database_model: Menu | Submenu | Dish,
        session: AsyncSession = Depends(get_async_session)
) -> dict[Any, Any]:
    """
    Функция для внесения данных в БД.

    Args:
        data_dict: сформированный словарь на основе данных, полученных из запроса
        database_model: модель данных, для которой создается запись
        session: сессия подключения к БД.

    Returns: словарь, построенный на основе созданного объекта (новой записи в БД)

    """

    stmt = insert(database_model).values(data_dict).returning(database_model)

    result = await session.execute(stmt)

    created_object = result.scalars().all()[0]

    created_object_dict = get_created_object_dict(
        created_object=created_object)

    await session.commit()

    return created_object_dict


async def select_all_menus_detail(session: AsyncSession = Depends(get_async_session)) -> list[Menu]:
    """
    Осуществляет выборку всех меню со всеми связанными подменю и блюдами;

    :param session: сессия подключения к БД
    :return: список со всеми меню с отображением привязанных подменю и блюд
    """

    stmt = select(Menu).outerjoin(Submenu, Submenu.menu_id == Menu.id).options(joinedload(Menu.submenus))
    result: Result = await session.execute(stmt)

    menus = result.unique().scalars().all()

    return menus


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

    result = await session.execute(stmt)

    updated_menu = result.scalars().all()[0]

    await session.commit()

    return updated_menu


async def delete_menu(
        target_menu_id: str | None = None,
        session: AsyncSession = Depends(get_async_session)
) -> None:
    """
    Функция для удаления записи из БД.

    Args:
        target_menu_id: id записи, которую необходимо удалить
        session: сессия подключения к БД.

    Returns: None

    """
    if target_menu_id is None:
        stmt = delete(Menu)
    else:
        stmt = delete(Menu).where(cast(Menu.id == target_menu_id, Boolean))

    await session.execute(stmt)

    await session.commit()


async def get_dishes_for_submenu(
        target_submenu_id: str, session: AsyncSession = Depends(get_async_session)
) -> list[Dish]:
    """
    Получает блюда для подменю

    :param target_submenu_id: id подменю
    :param session: сессия подключения к БД.
    :return: список блюд
    """
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


async def select_all_dishes(
        target_menu_id: str,
        target_submenu_id: str,
        session: AsyncSession = Depends(get_async_session),
) -> list[type[Dish]]:
    """
    Функция для получения всех блюд по указанному id меню и привязанного к нему подменю.

    Args:
        target_menu_id: идентификатор меню, к которому должно быть привязано подменю.
        target_submenu_id: идентификатор подменю, к которому должно быть привязано блюдо
        session: сессия подключения к БД.

    Returns: объект с информацией о найденных блюдах.

    """

    stmt = (
        select(Dish)
        .join(Submenu)
        .where(
            and_(
                Submenu.menu_id == target_menu_id, Dish.submenu_id == target_submenu_id
            )
        )
    )

    result: Result = await session.execute(stmt)

    dishes = result.scalars().all()

    return dishes


async def select_specific_dish(
        target_menu_id: str,
        target_submenu_id: str,
        target_dish_id: str,
        session: AsyncSession = Depends(get_async_session),
) -> Result[tuple[Dish]] | bool:
    """
    Функция для получения определенного блюда по указанному id меню и привязанного к нему подменю, а также по-указанному
    id блюда.

    Args:
        target_menu_id: идентификатор меню, к которому должно быть привязано подменю.
        target_submenu_id: идентификатор подменю, к которому должно быть привязано блюдо.
        target_dish_id: идентификатор искомого блюда.
        session: сессия подключения к БД.

    Returns: результат поиска.

    """

    try:
        # Формируем SQL код для поиска блюда, id которого равен указанному.
        # А также id menu и id submenu равны указанным в запросе.
        stmt = (
            select(Dish)
            .join(Submenu)
            .where(
                and_(
                    Submenu.menu_id == target_menu_id,
                    Dish.submenu_id == target_submenu_id,
                    Dish.id == target_dish_id,
                )
            )
        )
    except DBAPIError:
        '''Ошибка может возникнуть, если делать запрос к блюду с некорректными target_menu_id или target_submenu_id'''
        return False

    result = await session.execute(stmt)

    return result


async def update_dish(
        target_submenu_id: str,
        target_dish_id: str,
        update_data: UpdateDish,
        session: AsyncSession = Depends(get_async_session),
) -> Dish:
    """
    Функция для обновления данных в БД.

    Args:
        target_submenu_id: идентификатор подменю, к которому должно быть привязано блюдо.
        target_dish_id: идентификатор обновляемого блюда.
        update_data: данные, на которые нужно обновить текущие.
        session: сессия подключения к БД.

    Returns: объект с обновленными данными.

    """

    # Формируем SQL код, который найдет блюдо с submenu_id == target_submenu_id и id == target_dish_id
    stmt = (
        update(Dish)
        .where(and_(Dish.submenu_id == target_submenu_id, Dish.id == target_dish_id))
        .values(**update_data.model_dump())
    ).returning(Dish)

    result = await session.execute(stmt)

    updated_dish: Dish = result.scalars().all()[0]

    await session.commit()

    return updated_dish


async def delete_dish(
        target_submenu_id: str,
        target_dish_id: str,
        session: AsyncSession = Depends(get_async_session),
) -> None:
    """
    Функция для удаления данных из БД.

    Args:
        target_submenu_id: идентификатор подменю, к которому должно быть привязано блюдо.
        target_dish_id: идентификатор удаляемого блюда.
        session: сессия подключения к БД.

    Returns: None

    """
    stmt = delete(Dish).where(
        and_(Dish.submenu_id == target_submenu_id, Dish.id == target_dish_id)
    )

    await session.execute(stmt)

    await session.commit()


async def select_submenus_for_menu(
        submenu: Submenu,
        target_menu_id: str,
        session: AsyncSession = Depends(get_async_session),
) -> list[Submenu]:
    """
    Получает все подменю для меню, id которого было передано

    Args:
        submenu: класс модели БД Submenu,
        target_menu_id: идентификатор меню, к которому должно быть привязано подменю,
        session: сессия подключения к БД,
        target_submenu_id: идентификатор подменю, к которому должно быть привязано блюдо
    :return:
        Список с найденным подменю или пустой список.
    """
    # Формируем запрос для нахождения всех подменю, которые привязаны к меню с id равным target_menu_id.
    stmt_submenus_linked_to_target_menu_id = select(submenu).where(
        cast(submenu.menu_id == target_menu_id, Boolean)
    )

    result_submenus_linked_to_target_menu_id = await session.execute(
        stmt_submenus_linked_to_target_menu_id
    )

    submenus_linked_to_target_menu_id = (
        result_submenus_linked_to_target_menu_id.scalars().all()
    )

    return submenus_linked_to_target_menu_id
