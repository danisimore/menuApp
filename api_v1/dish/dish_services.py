"""
Бизнес логика, специфичная для модуля.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 06 февраля 2024
"""
from typing import Any

from database.database import get_async_session
from dish.models import Dish
from dish.schemas import UpdateDish
from fastapi import Depends
from sqlalchemy import (
    Boolean,
    ChunkedIteratorResult,
    Result,
    and_,
    cast,
    delete,
    select,
    update,
)
from sqlalchemy.exc import DBAPIError
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
    # Формируем запрос для нахождения всех подменю, которые привязаны к меню с id равным target_menu_id.
    stmt_submenus_linked_to_target_menu_id = select(submenu).where(
        cast(submenu.menu_id == target_menu_id, Boolean)
    )
    # Исполняем запрос.
    result_submenus_linked_to_target_menu_id = await session.execute(
        stmt_submenus_linked_to_target_menu_id
    )
    # Получаем список найденных объектов (Подменю, привязанных к target_menu_id).
    submenus_linked_to_target_menu_id = (
        result_submenus_linked_to_target_menu_id.scalars().all()
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
