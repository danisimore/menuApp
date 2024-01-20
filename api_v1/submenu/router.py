from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select, insert, cast, Boolean, Result
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_async_session
from menu.utils import get_created_object_dict
from submenu.models import Submenu

from .schemas import CreateSubmenu

router = APIRouter(prefix="/api/v1/menus", tags=["submenu"])


@router.get("/{target_menu_id}/submenus")
async def get_menu_submenus(target_menu_id, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Submenu).where(cast(Submenu.menu_id == target_menu_id, Boolean))

    result: Result = await session.execute(stmt)

    submenus = result.scalars().all()

    return submenus


@router.post("/{target_menu_id}/submenus")
async def create_submenu(
        target_menu_id,
        submenu_data: CreateSubmenu,
        session: AsyncSession = Depends(get_async_session)
):
    submenu_data_dict = submenu_data.model_dump()
    submenu_data_dict["menu_id"] = target_menu_id
    stmt = insert(Submenu).values(submenu_data_dict).returning(Submenu)

    result = await session.execute(stmt)

    created_submenu = result.scalars().all()[0]

    created_submenu_dict = get_created_object_dict(created_object=created_submenu)

    await session.commit()

    return JSONResponse(content=created_submenu_dict, status_code=201)

