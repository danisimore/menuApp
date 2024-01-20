from fastapi import APIRouter, Depends
from sqlalchemy import select, cast, Boolean, Result
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_async_session
from submenu.models import Submenu

router = APIRouter(prefix="/api/v1/menus", tags=["submenu"])


@router.get("/{target_menu_id}/submenus")
async def get_menu_submenus(target_menu_id, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Submenu).where(cast(Submenu.id == target_menu_id, Boolean))

    result: Result = await session.execute(stmt)

    submenus = result.scalars().all()

    return submenus
