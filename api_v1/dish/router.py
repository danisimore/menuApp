"""
Модуль для обработки POST, GET, UPDATE, PATCH, DELETE методов для эндпоинтов, касающихся блюд.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 22 января 2024
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession

from services import insert_data
from utils import get_created_object_dict

from database.database import get_async_session

from dish.models import Dish
from dish.schemas import CreateDish, UpdateDish
from dish.dish_services import (
    is_submenu_in_target_menu,
    select_all_dishes,
    select_specific_dish,
    update_dish,
    delete_dish,
)
from dish.dish_utils import format_decimal, return_404_menu_not_linked_to_submenu

from submenu.models import Submenu

router = APIRouter(prefix="/api/v1/menus", tags=["Dish"])


@router.get("/{target_menu_id}/submenus/{target_submenu_id}/dishes")
async def dish_get_method(
    target_menu_id: str,
    target_submenu_id: str,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Функция для обработки get запроса для получения блюд привязанных к подменю.

    Args:
        target_menu_id: идентификатор меню, к которому привязано submenu
        target_submenu_id: идентификатор подменю, к которому привязано блюдо
        session:

    Returns: Список объектов найденных блюд.

    """

    dishes = await select_all_dishes(
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
        session=session,
    )

    return dishes


@router.post("/{target_menu_id}/submenus/{target_submenu_id}/dishes")
async def dish_post_method(
    target_menu_id: str,
    target_submenu_id: str,
    dish_data: CreateDish,
    session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    """
    Функция для обработки POST запроса.

    Args:
        target_menu_id: идентификатор меню с привязанным подменю, в котором создается блюдо;
        target_submenu_id: идентификатор подменю, в котором создается блюдо;
        dish_data: данные, которые должны записаться в новой записи в таблице dishes;
        session: сессия подключения к БД.

    Returns: JSONResponse.

    """

    # Проверяем привязано ли указанное подменю к указанному меню.
    submenu_in_target_menu = await is_submenu_in_target_menu(
        submenu=Submenu,
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
        session=session,
    )

    # Если не привязано, то возвращаем 404
    if not submenu_in_target_menu:
        return return_404_menu_not_linked_to_submenu()

    # Формируем словарь из полученных данных.
    dish_data_dict = dish_data.model_dump()
    # Указываем, что блюдо привязывается у указанному в запросе подменю.
    dish_data_dict["submenu_id"] = target_submenu_id

    created_dish_dict = await insert_data(
        data_dict=dish_data_dict, database_model=Dish, session=session
    )

    return JSONResponse(content=created_dish_dict, status_code=201)


@router.get("/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}")
async def dish_get_specific_method(
    target_menu_id: str,
    target_submenu_id: str,
    target_dish_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    """
    Функция для получения определенного блюда.

    Args:
        target_menu_id: идентификатор меню с привязанным подменю, в котором создается блюдо.
        target_submenu_id: идентификатор подменю, в котором создается блюдо.
        target_dish_id: идентификатор блюда, которое необходимо получить.
        session: сессия подключения к БД.

    Returns: JSONResponse

    """

    result = await select_specific_dish(
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
        target_dish_id=target_dish_id,
        session=session,
    )

    try:
        dish = result.scalars().all()[0]
    except IndexError:
        return JSONResponse(content={"detail": "dish not found"}, status_code=404)

    # Формируем словарь, чтобы корректно отобразить цену (2 знака после запятой).
    dish_dict = {
        "id": str(dish.id),
        "title": dish.title,
        "description": dish.description,
        "price": format_decimal(dish.price),
        "submenu_id": str(dish.submenu_id),
    }

    return JSONResponse(content=dish_dict)


@router.patch("/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}")
async def dish_patch_method(
    target_menu_id: str,
    target_submenu_id: str,
    target_dish_id: str,
    dish_data: UpdateDish,
    session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    """
    Функция для обработки PATCH запроса.

    Args:
        target_menu_id: идентификатор меню с привязанным подменю, в котором создается блюдо.
        target_submenu_id: идентификатор подменю, в котором создается блюдо.
        target_dish_id: идентификатор блюда, которое необходимо получить.
        dish_data: новые данные для найденной записи в таблице dishes,
        session: сессия подключения к БД.

    Returns: JSONResponse

    """

    # Проверяем привязано ли указанное подменю к указанному меню.
    submenu_in_target_menu = await is_submenu_in_target_menu(
        submenu=Submenu,
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
        session=session,
    )

    # Если не привязано, то возвращаем 404
    if not submenu_in_target_menu:
        return return_404_menu_not_linked_to_submenu()

    updated_dish = await update_dish(
        target_dish_id=target_dish_id,
        target_submenu_id=target_submenu_id,
        update_data=dish_data,
        session=session,
    )

    updated_dish_dict = get_created_object_dict(updated_dish)

    return JSONResponse(content=updated_dish_dict, status_code=200)


@router.delete("/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}")
async def dish_delete_method(
    target_menu_id: str,
    target_submenu_id: str,
    target_dish_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    """
    Функция для обработки DELETE запроса.

    Args:
        target_menu_id: идентификатор меню с привязанным подменю, в котором создается блюдо.
        target_submenu_id: идентификатор подменю, в котором создается блюдо.
        target_dish_id: идентификатор блюда, которое необходимо удалить.
        session: сессия подключения к БД.

    Returns: JSONResponse

    """

    submenu_in_target_menu = await is_submenu_in_target_menu(
        submenu=Submenu,
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
        session=session,
    )

    if not submenu_in_target_menu:
        return return_404_menu_not_linked_to_submenu()

    await delete_dish(
        target_dish_id=target_dish_id,
        target_submenu_id=target_submenu_id,
        session=session,
    )

    return JSONResponse(content={"status": "Success!"}, status_code=200)
