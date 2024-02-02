"""
Модуль для обработки POST, GET, UPDATE, PATCH, DELETE методов для эндпоинтов, касающихся меню.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 29 января 2024 - добавлено преобразование цен блюд из Decimal к строке
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_async_session
from services import insert_data
from utils import get_created_object_dict
from .menu_services import (
    select_all_menus,
    select_specific_menu,
    update_menu,
    delete_menu,
)

from .schemas import MenuCreate, MenuUpdate
from .models import Menu

from redis_tools.tools import RedisTools


router = APIRouter(prefix="/api/v1", tags=["Menu"])
redis = RedisTools()


@router.get("/menus")
async def menu_get_method(session: AsyncSession = Depends(get_async_session)):
    """
    Функция для обработки get запроса для получения всех меню.

    Args:
        session: сессия подключения к БД.

    Returns: список объектов найденных меню.

    """

    cache = await redis.get_pair(key="menus")

    if cache is not None:
        return cache

    menus = await select_all_menus(session=session)

    await redis.set_pair(key="menus", value=menus)

    return menus


@router.post("/menus")
async def menu_post_method(
    new_menu_data: MenuCreate, session: AsyncSession = Depends(get_async_session)
) -> JSONResponse:
    """
    Функция для обработки POST запроса.

    Args:
        new_menu_data: данные для создания новой записи в таблице menu;
        session: сессия подключения к БД.

    Returns: JSONResponse.

    """

    new_menu_data_dict = new_menu_data.model_dump()
    created_menu = await insert_data(
        data_dict=new_menu_data_dict, database_model=Menu, session=session
    )

    await redis.invalidate_cache(key="menus")

    return JSONResponse(content=created_menu, status_code=201)


@router.get("/menus/{target_menu_id}")
async def menu_get_specific_method(
    target_menu_id, session: AsyncSession = Depends(get_async_session)
):
    """
    Функция для обработки get запроса по указанному id.

    Args:
        target_menu_id: идентификатор записи, данные о которой необходимо получить;
        session: сессия подключения к БД.

    Returns: Объект найденной по id записи.

    """

    cache = await redis.get_pair(key=target_menu_id)

    if cache is not None:
        print("Hello from cache!")
        if cache.get("404"):
            return JSONResponse(content={"detail": "menu not found"}, status_code=404)
        return cache

    menu_data = await select_specific_menu(
        target_menu_id=target_menu_id, session=session
    )

    if menu_data:
        menu = menu_data[0][0]
        menu.submenus_count = menu_data[0][1]
        menu.dishes_count = menu_data[0][2]

        await redis.set_pair(key=target_menu_id, value=menu.json())

        return menu
    else:
        await redis.set_pair(key=target_menu_id, value={"404": "not_found"})
        return JSONResponse(content={"detail": "menu not found"}, status_code=404)


@router.patch("/menus/{target_menu_id}")
async def menu_patch_method(
    target_menu_id: str,
    update_menu_data: MenuUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> JSONResponse:
    """
    Функция для обработки запроса с методом PATCH.

    Args:
        target_menu_id: id записи, которую необходимо обновить
        update_menu_data: данные, на которые будут заменены текущие
        session: сессия подключения к БД.

    Returns: JSONResponse, который содержит объект обновленной записи и статус код.

    """

    # Получаем объект созданной записи.
    updated_menu = await update_menu(
        update_menu_data=update_menu_data,
        target_menu_id=target_menu_id,
        session=session,
    )

    # Формируем словарь на основе этого объекта.
    updated_menu_dict = get_created_object_dict(created_object=updated_menu)

    await redis.invalidate_cache(key="menus")
    await redis.invalidate_cache(key=target_menu_id)

    return JSONResponse(content=updated_menu_dict, status_code=200)


@router.delete("/menus/{target_menu_id}")
async def menu_delete_method(
    target_menu_id, session: AsyncSession = Depends(get_async_session)
) -> JSONResponse:
    """
    Функция для обработки запроса с методом DELETE.

    Args:
        target_menu_id: id записи, которую необходимо удалить
        session: сессия подключения к БД.

    Returns: JSONResponse

    """

    await delete_menu(target_menu_id=target_menu_id, session=session)

    await redis.invalidate_cache(key="menus")
    await redis.invalidate_cache(key=target_menu_id)

    return JSONResponse(content={"status": "success!"}, status_code=200)
