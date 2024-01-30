"""
Модуль для обработки POST, GET, UPDATE, PATCH, DELETE методов для эндпоинтов, касающихся подменю.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 22 января 2024
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_async_session
from services import insert_data
from utils import get_created_object_dict

from submenu.models import Submenu

from .schemas import CreateSubmenu, UpdateSubmenu
from .submenu_services import (
    select_all_submenus,
    select_specific_submenu,
    update_submenu,
    delete_submenu,
    get_dishes_for_submenu
)

from .submenu_utils import convert_prices_to_str


router = APIRouter(prefix="/api/v1/menus", tags=["submenu"])


@router.get("/{target_menu_id}/submenus")
async def submenu_get_method(
    target_menu_id: str, session: AsyncSession = Depends(get_async_session)
):
    """
    Функция для обработки get запроса для выборки всех подменю, связанных с указанным меню.

    Args:
        target_menu_id: идентификатор меню, для которого идет поиск подменю
        session: сессия подключения к БД.

    Returns: Список найденных объектов подменю.

    """

    submenus = await select_all_submenus(target_menu_id=target_menu_id, session=session)

    return submenus


@router.post("/{target_menu_id}/submenus")
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

    submenu_data_dict = submenu_data.model_dump()
    submenu_data_dict["menu_id"] = target_menu_id

    created_submenu = await insert_data(
        data_dict=submenu_data_dict, database_model=Submenu, session=session
    )

    submenu_dishes = await get_dishes_for_submenu(created_submenu["id"], session=session)

    created_submenu["dishes"] = submenu_dishes

    return JSONResponse(content=created_submenu, status_code=201)


@router.get("/{target_menu_id}/submenus/{target_submenu_id}")
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
    try:
        submenu = await select_specific_submenu(
            target_menu_id=target_menu_id,
            target_submenu_id=target_submenu_id,
            session=session,
        )
        # Если подменю было найдено, то получаем его из списка.
        submenu = submenu[0]
    except IndexError:
        return JSONResponse(content={"detail": "submenu not found"}, status_code=404)

    convert_prices_to_str(submenu=submenu)

    return submenu


@router.patch("/{target_menu_id}/submenus/{target_submenu_id}")
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

    try:
        updated_submenu = updated_submenu[0]
        updated_submenu_dict = get_created_object_dict(updated_submenu)

        submenu_dishes = await get_dishes_for_submenu(target_submenu_id, session=session)

        updated_submenu_dict["dishes"] = submenu_dishes

    except IndexError:
        return JSONResponse(
            content={"detail": "no submenu was found for the specified data"},
            status_code=404,
        )

    return JSONResponse(content=updated_submenu_dict, status_code=200)


@router.delete("/{target_menu_id}/submenus/{target_submenu_id}")
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

    await delete_submenu(
        target_submenu_id=target_submenu_id,
        target_menu_id=target_menu_id,
        session=session,
    )

    return JSONResponse(content={"status": "success!"}, status_code=200)
