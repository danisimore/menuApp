"""
Модуль для обработки POST, GET, UPDATE, PATCH, DELETE методов для эндпоинтов, касающихся меню.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru

Дата: 10 февраля 2024 | Реализована инвалидация кэша для синхронизации с Google Sheets
"""
from typing import Any

from custom_router import CustomAPIRouter
from database.database import get_async_session
from database.database_services import (
    delete_menu,
    insert_data,
    select_all_menus,
    select_all_menus_detail,
    select_all_submenus,
    select_specific_menu,
    update_menu,
)
from fastapi import BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from services import (
    create_cache,
    delete_cache_by_key,
    delete_linked_menu_cache,
    get_cache,
)
from sqlalchemy.ext.asyncio import AsyncSession
from utils import get_created_object_dict

from .menu_services import parse_menu_data
from .menu_utils import format_detailed_menus
from .models import Menu
from .schemas import MenuCreate, MenusGet, MenuSpecificGet, MenuUpdate

router = CustomAPIRouter(prefix='/api/v1', tags=['Menu'])


@router.get(path='/menus/detail')
async def get_all_menus_detail(session: AsyncSession = Depends(get_async_session)) -> list[dict[Any, Any]]:
    """
    Обработка GET запроса для вывода всех меню со всеми связанными подменю и со всеми связанными блюдами

    :param session: сессия подключения к БД
    :return: список со всеми меню с отображением привязанных подменю и блюд
    """

    cache = await get_cache(key='menus_detail')

    if cache is not None:
        return cache

    menus = await select_all_menus_detail(session=session)

    menus_json = await format_detailed_menus(menus=menus, session=session)
    await create_cache(key='menus_detail', value=menus_json)

    return menus_json


@router.get(path='/menus', name='menu_base_url')
async def menu_get_method(session: AsyncSession = Depends(get_async_session)) -> list[MenusGet]:
    """
    Функция для обработки get запроса для получения всех меню.

    Args:
        session: сессия подключения к БД.

    Returns: список объектов найденных меню.

    """

    cache = await get_cache(key='menus')

    if cache is not None:
        return cache

    menus = await select_all_menus(session=session)

    await create_cache(key='menus', value=menus)

    return menus


@router.post(path='/menus')
async def menu_post_method(
    new_menu_data: MenuCreate, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_async_session)
) -> JSONResponse:
    """
    Функция для обработки POST запроса.

    Args:
        new_menu_data: данные для создания новой записи в таблице menu;
        background_tasks: Объект фоновых задач FastAPI.
        session: сессия подключения к БД.

    Returns: JSONResponse.

    """

    new_menu_data_dict = new_menu_data.model_dump()
    created_menu = await insert_data(
        data_dict=new_menu_data_dict, database_model=Menu, session=session
    )

    background_tasks.add_task(delete_cache_by_key, 'menus')
    background_tasks.add_task(delete_cache_by_key, 'menus_detail')
    background_tasks.add_task(delete_cache_by_key, 'table_cache')

    return JSONResponse(content=created_menu, status_code=201)


@router.get(path='/menus/{target_menu_id}')
async def menu_get_specific_method(
    target_menu_id: str, session: AsyncSession = Depends(get_async_session)
) -> MenuSpecificGet:
    """
    Функция для обработки get запроса по указанному id.

    Args:
        target_menu_id: идентификатор записи, данные о которой необходимо получить;
        session: сессия подключения к БД.

    Returns: Объект найденной по id записи.

    """

    cache = await get_cache(key=target_menu_id)

    if cache is not None:
        return cache

    menu_data = await select_specific_menu(
        target_menu_id=target_menu_id, session=session
    )

    menu = await parse_menu_data(menu_data=menu_data)

    if not menu:
        return JSONResponse(content={'detail': 'menu not found'}, status_code=404)

    menu_json = await menu.json()
    await create_cache(key=target_menu_id, value=menu_json)

    return menu


@router.patch('/menus/{target_menu_id}')
async def menu_patch_method(
    target_menu_id: str,
    update_menu_data: MenuUpdate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    """
    Функция для обработки запроса с методом PATCH.

    Args:
        target_menu_id: id записи, которую необходимо обновить
        update_menu_data: данные, на которые будут заменены текущие
        background_tasks: Объект фоновых задач FastAPI.
        session: сессия подключения к БД.

    Returns: JSONResponse, который содержит объект обновленной записи и статус код.

    """

    updated_menu = await update_menu(
        update_menu_data=update_menu_data,
        target_menu_id=target_menu_id,
        session=session,
    )

    updated_menu_dict = get_created_object_dict(created_object=updated_menu)

    background_tasks.add_task(delete_cache_by_key, 'menus')
    background_tasks.add_task(delete_cache_by_key, target_menu_id)
    background_tasks.add_task(delete_cache_by_key, 'menus_detail')

    background_tasks.add_task(delete_cache_by_key, 'table_cache')

    return JSONResponse(content=updated_menu_dict, status_code=200)


@router.delete('/menus/{target_menu_id}')
async def menu_delete_method(
    target_menu_id: str, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_async_session)
) -> JSONResponse:
    """
    Функция для обработки запроса с методом DELETE.

    Args:
        target_menu_id: id записи, которую необходимо удалить
        background_tasks: Объект фоновых задач FastAPI
        session: сессия подключения к БД.

    Returns: JSONResponse

    """
    submenus_for_menu = await select_all_submenus(session=session, target_menu_id=target_menu_id)

    await delete_linked_menu_cache(
        submenus_for_menu=submenus_for_menu,
        target_menu_id=target_menu_id,
        background_tasks=background_tasks,
        session=session
    )

    await delete_menu(target_menu_id=target_menu_id, session=session)

    background_tasks.add_task(delete_cache_by_key, target_menu_id)
    background_tasks.add_task(delete_cache_by_key, 'menus')
    background_tasks.add_task(delete_cache_by_key, 'menus_detail')

    return JSONResponse(content={'status': 'success!'}, status_code=200)
