"""
Модуль для обработки POST, GET, UPDATE, PATCH, DELETE методов для эндпоинтов, касающихся блюд.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru

Дата: 11 февраля 2024 | Добавлена очистка кэша с инфой о синхронизации с таблицей при выполнении CUD методов
"""

from custom_router import CustomAPIRouter
from database.database import get_async_session
from database.database_services import (
    delete_dish,
    select_all_dishes,
    select_specific_dish,
    update_dish,
)
from dish.dish_services import (
    generate_dish_dict,
    is_submenu_in_target_menu,
    try_get_dish,
)
from dish.dish_utils import apply_discount, return_404_menu_not_linked_to_submenu
from dish.models import Dish
from dish.schemas import CreateDish, UpdateDish
from fastapi import Depends
from fastapi.responses import JSONResponse
from services import (
    create_cache,
    delete_cache,
    delete_cache_by_key,
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

    formatted_dishes = await format_dishes(dishes)
    dishes_with_discount = await apply_discount(formatted_dishes)

    await create_cache(key=cache_key, value=dishes_with_discount)

    return dishes_with_discount


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

    if not submenu_in_target_menu:
        return return_404_menu_not_linked_to_submenu()

    dish_data_dict = create_dict_from_received_data(
        received_data=dish_data,
        parent_id=target_submenu_id,
        foreign_key_field_name='submenu_id',
    )

    created_dish_dict = await insert_data(
        data_dict=dish_data_dict, database_model=Dish, session=session
    )

    dishes_cache_key = target_menu_id + '_' + target_submenu_id + '_dishes'
    submenus_cache_key = target_menu_id + '_submenus'

    await delete_cache(key=dishes_cache_key)
    await delete_cache_by_key(key='menus_detail')
    await delete_cache_by_key(key=target_menu_id)
    await delete_cache_by_key(key=submenus_cache_key)
    await delete_cache_by_key(key=target_submenu_id)
    await delete_cache_by_key(key='table_cache')

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

    if not dish:
        return JSONResponse(content={'detail': 'dish not found'}, status_code=404)

    dish_dict = await generate_dish_dict(dish=dish)

    dish_dict_with_discount = await apply_discount(dishes=[dish_dict])

    await create_cache(key=cache_key, value=dish_dict_with_discount)
    return JSONResponse(content=dish_dict_with_discount[0])


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

    submenu_in_target_menu = await is_submenu_in_target_menu(
        submenu=Submenu,
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
        session=session,
    )

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
    submenus_cache_key = target_menu_id + '_submenus'

    await delete_cache_by_key(key=cache_key_all_dishes_for_submenu)
    await delete_cache_by_key(key=cache_key_specific_dish)
    await delete_cache_by_key(key='menus_detail')

    await delete_cache_by_key(key=submenus_cache_key)
    await delete_cache_by_key(key=target_submenu_id)
    await delete_cache_by_key(key='table_cache')

    updated_dish_dict_with_discount = await apply_discount(dishes=[updated_dish_dict])

    return JSONResponse(content=updated_dish_dict_with_discount[0], status_code=200)


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

    all_dishes_for_submenu_cache_key = target_menu_id + '_' + target_submenu_id + '_dishes'
    specific_dish_cache_key = target_menu_id + '_' + target_submenu_id + '_' + target_dish_id
    submenus_cache_key = target_menu_id + '_submenus'

    await delete_cache_by_key(key=all_dishes_for_submenu_cache_key)
    await delete_cache_by_key(key=specific_dish_cache_key)
    await delete_cache_by_key(key=target_submenu_id)
    await delete_cache_by_key(key=submenus_cache_key)
    await delete_cache_by_key(key=target_menu_id)
    await delete_cache_by_key(key='menus_detail')
    await delete_cache_by_key(key='table_cache')

    return JSONResponse(content={'status': 'success!'}, status_code=200)
