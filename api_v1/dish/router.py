"""
Модуль для обработки POST, GET, UPDATE, PATCH, DELETE методов для эндпоинтов, касающихся блюд.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 06 февраля 2024
"""

from custom_router import CustomAPIRouter
from database.database import get_async_session
from dish.dish_services import (
    delete_dish,
    generate_dish_dict,
    is_submenu_in_target_menu,
    select_all_dishes,
    select_specific_dish,
    try_get_dish,
    update_dish,
)
from dish.dish_utils import return_404_menu_not_linked_to_submenu
from dish.models import Dish
from dish.schemas import CreateDish, UpdateDish
from fastapi import Depends
from fastapi.responses import JSONResponse
from services import (
    create_cache,
    delete_all_cache,
    delete_cache,
    get_cache,
    insert_data,
)
from sqlalchemy.ext.asyncio import AsyncSession
from submenu.models import Submenu
from submenu.submenu_utils import format_dishes
from utils import create_dict_from_received_data, get_created_object_dict

router = CustomAPIRouter(prefix='/api/v1/menus', tags=['Dish'])


@router.get('/{target_menu_id}/submenus/{target_submenu_id}/dishes', name='dish_base_url')
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
    cache_key = target_menu_id + '_' + target_submenu_id + '_dishes'

    cache = await get_cache(key=cache_key)

    if cache is not None:
        return cache

    dishes = await select_all_dishes(
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
        session=session,
    )

    await create_cache(key=cache_key, value=dishes)

    formatted_dishes = await format_dishes(dishes)

    return formatted_dishes


@router.post('/{target_menu_id}/submenus/{target_submenu_id}/dishes')
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
    dish_data_dict = create_dict_from_received_data(
        received_data=dish_data,
        parent_id=target_submenu_id,
        foreign_key_field_name='submenu_id',
    )

    created_dish_dict = await insert_data(
        data_dict=dish_data_dict, database_model=Dish, session=session
    )

    cache_key = target_menu_id + '_' + target_submenu_id + '_dishes'

    await delete_cache(key=cache_key)

    return JSONResponse(content=created_dish_dict, status_code=201)


@router.get('/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}')
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

    cache_key = target_menu_id + '_' + target_submenu_id + '_' + target_dish_id

    cache = await get_cache(key=cache_key)

    if cache is not None:
        return cache

    result = await select_specific_dish(
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
        target_dish_id=target_dish_id,
        session=session,
    )

    dish = await try_get_dish(result=result)

    # Если блюдо по указанным параметрам не найдено, то возвращаем 404, иначе json с данными об этом блюде
    if not dish:
        return JSONResponse(content={'detail': 'dish not found'}, status_code=404)

    dish_dict = await generate_dish_dict(dish=dish)
    await create_cache(key=cache_key, value=dish_dict)
    return JSONResponse(content=dish_dict)


@router.patch('/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}')
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

    cache_key_all_dishes_for_submenu = target_menu_id + '_' + target_submenu_id + '_dishes'
    cache_key_specific_dish = target_menu_id + '_' + target_submenu_id + '_' + target_dish_id

    await delete_cache(key=cache_key_all_dishes_for_submenu)
    await delete_cache(key=cache_key_specific_dish)

    return JSONResponse(content=updated_dish_dict, status_code=200)


@router.delete('/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}')
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

    await delete_all_cache()

    return JSONResponse(content={'status': 'success!'}, status_code=200)
