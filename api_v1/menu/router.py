"""
Модуль для обработки POST, GET, UPDATE, PATCH, DELETE методов для эндпоинтов, касающихся меню.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 22 января 2024
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_async_session
from services import insert_data
from submenu.models import Submenu
from utils import get_created_object_dict
from .menu_services import (
    select_all_menus,
    select_specific_menu,
    update_menu,
    delete_menu,
)

from .schemas import MenuCreate, MenuUpdate
from .models import Menu
from .menu_utils import count_dishes

router = APIRouter(prefix="/api/v1", tags=["Menu"])


@router.get("/menus")
async def menu_get_method(session: AsyncSession = Depends(get_async_session)):
    """
    Функция для обработки get запроса для получения всех меню.

    Args:
        session: сессия подключения к БД.

    Returns: список объектов найденных меню.

    """

    menus = await select_all_menus(session=session)

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

    menu = await select_specific_menu(
        target_menu_id=target_menu_id, submenu=Submenu, session=session
    )

    if menu:
        # Если меню нашлось, то задаем атрибут submenus_count для отображения его в теле ответа
        menu.submenus_count = menu.submenu_count

        # Считаем кол-во блюд, привязанных к текущему меню через привязанные к нему подменю.
        dishes = count_dishes(menu=menu)

        # Устанавливаем атрибут, отображающий в теле ответа кол-во блюд в меню.
        menu.dishes_count = dishes

        return menu
    else:
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

    return JSONResponse(content={"status": "success!"}, status_code=200)
