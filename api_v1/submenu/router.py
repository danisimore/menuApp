"""
Модуль для обработки POST, GET, UPDATE, PATCH, DELETE методов для эндпоинтов, касающихся подменю.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 11 февраля 2024 | Добавлена очистка кэша с инфой о синхронизации с таблицей при выполнении CUD методов.
"""
from typing import Any

from custom_router import CustomAPIRouter
from database.database import get_async_session
from database.database_services import (
    delete_submenu,
    get_dishes_for_submenu,
    select_all_submenus,
    select_specific_submenu,
    update_submenu,
)
from dish.dish_utils import apply_discount
from fastapi import Depends
from fastapi.responses import JSONResponse
from services import (
    create_cache,
    delete_cache,
    delete_cache_by_key,
    delete_linked_submenu_cache,
    get_cache,
    insert_data,
)
from sqlalchemy.ext.asyncio import AsyncSession
from submenu.models import Submenu
from submenu.submenu_utils import format_dishes
from utils import create_dict_from_received_data, get_created_object_dict

from .schemas import CreateSubmenu, UpdateSubmenu
from .submenu_services import prepare_submenu_to_response, prepare_submenus_to_response

router = CustomAPIRouter(prefix='/api/v1/menus', tags=['submenu'])


@router.get('/{target_menu_id}/submenus', name='submenu_base_url')
async def submenu_get_method(
        target_menu_id: str, session: AsyncSession = Depends(get_async_session)
) -> list[dict[Any, Any]]:
    """
    Функция для обработки get запроса для выборки всех подменю, связанных с указанным меню.

    Args:
        target_menu_id: идентификатор меню, для которого идет поиск подменю
        session: сессия подключения к БД.

    Returns: Список найденных объектов подменю.

    """

    cache_key = target_menu_id + '_submenus'

    cache = await get_cache(key=cache_key)

    if cache is not None:
        return cache

    submenus = await select_all_submenus(target_menu_id=target_menu_id, session=session)

    # Форматируем Submenu, чтобы в ответе цены блюд были строками и учитывали скидку.
    formatted_submenus = await prepare_submenus_to_response(submenus=submenus, session=session)

    await create_cache(key=cache_key, value=submenus)

    return formatted_submenus


@router.post('/{target_menu_id}/submenus')
async def submenu_post_method(
        target_menu_id: str,
        submenu_data: CreateSubmenu,
        session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    """
    Функция для обработки POST запроса.

    Args:
        target_menu_id: идентификатор меню, с которым будет связано созданное подменю
        submenu_data: данные подменю, которое будет создано
        session: сессия подключения к БД.

    Returns:JSONResponse

    """

    submenu_data_dict = create_dict_from_received_data(
        received_data=submenu_data,
        parent_id=target_menu_id,
        foreign_key_field_name='menu_id',
    )

    created_submenu = await insert_data(
        data_dict=submenu_data_dict, database_model=Submenu, session=session
    )

    submenu_dishes = await get_dishes_for_submenu(
        created_submenu['id'], session=session
    )

    created_submenu['dishes'] = await format_dishes(submenu_dishes)

    cache_key = target_menu_id + '_submenus'

    await delete_cache(key=cache_key)
    await delete_cache_by_key(key='menus_detail')
    await delete_cache_by_key(key=target_menu_id)
    await delete_cache_by_key(key='table_cache')

    return JSONResponse(content=created_submenu, status_code=201)


@router.get('/{target_menu_id}/submenus/{target_submenu_id}')
async def submenu_get_specific_method(
        target_menu_id: str,
        target_submenu_id: str,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Функция для обработки get запроса по-указанному id.

    Args:
        target_menu_id: идентификатор меню, с которым должно быть связанно искомое подменю
        target_submenu_id: идентификатор искомого подменю
        session: сессия подключения к БД.

    Returns: Если подменю найдено, то объект найденного подменю, если нет, то 404

    """

    cache = await get_cache(key=target_submenu_id)

    if cache is not None:
        return cache

    # Получаем определенное подменю
    submenu = await select_specific_submenu(
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
        session=session,
    )

    if not submenu:
        return JSONResponse(content={'detail': 'submenu not found'}, status_code=404)

    submenu_json = await prepare_submenu_to_response(submenu=submenu, session=session)

    await create_cache(key=target_submenu_id, value=submenu_json)

    return submenu_json


@router.patch('/{target_menu_id}/submenus/{target_submenu_id}')
async def submenu_patch_method(
        target_menu_id: str,
        target_submenu_id: str,
        update_submenu_data: UpdateSubmenu,
        session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    """
    Функция для обработки PATCH запроса по-указанному id.

    Args:
        target_menu_id: идентификатор меню, с которым должно быть связанно обновляемое подменю
        target_submenu_id: идентификатор обновляемого подменю
        update_submenu_data: данные, на которые нужно обновить текущие
        session: сессия подключения к БД.

    Returns: JSONResponse

    """

    updated_submenu = await update_submenu(
        target_submenu_id=target_submenu_id,
        target_menu_id=target_menu_id,
        update_submenu_data=update_submenu_data,
        session=session,
    )

    if len(updated_submenu) == 0:
        return JSONResponse(
            content={'detail': 'no submenu was found for the specified data'},
            status_code=404,
        )

    updated_submenu = updated_submenu[0]
    updated_submenu_dict = get_created_object_dict(updated_submenu)

    submenu_dishes = await get_dishes_for_submenu(
        target_submenu_id, session=session
    )

    submenu_formatted_dishes = await format_dishes(submenu_dishes)
    updated_submenu_dict['dishes'] = await apply_discount(submenu_formatted_dishes)

    all_submenus_for_menu_cache_key = target_menu_id + '_submenus'

    await delete_cache_by_key(key=all_submenus_for_menu_cache_key)
    await delete_cache_by_key(key=target_submenu_id)
    await delete_cache_by_key(key='menus_detail')
    await delete_cache_by_key(key='table_cache')

    return JSONResponse(content=updated_submenu_dict, status_code=200)


@router.delete('/{target_menu_id}/submenus/{target_submenu_id}')
async def submenu_delete_method(
        target_menu_id: str,
        target_submenu_id: str,
        session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    """
    Функция для обработки DELETE запроса по-указанному id.

    Args:
        target_menu_id: идентификатор меню, с которым должно быть связанно удаляемое подменю
        target_submenu_id: идентификатор удаляемого подменю
        session: сессия подключения к БД.

    Returns: JSONResponse

    """

    await delete_linked_submenu_cache(
        target_submenu_id=target_submenu_id,
        target_menu_id=target_menu_id,
        session=session
    )

    await delete_submenu(
        target_submenu_id=target_submenu_id,
        target_menu_id=target_menu_id,
        session=session,
    )

    all_submenus_for_menu_cache_key = target_menu_id + '_submenus'

    await delete_cache_by_key(key=target_submenu_id)
    await delete_cache_by_key(key=all_submenus_for_menu_cache_key)
    await delete_cache_by_key(key=target_menu_id)
    await delete_cache_by_key(key='menus_detail')
    await delete_cache_by_key(key='table_cache')

    return JSONResponse(content={'status': 'success!'}, status_code=200)
