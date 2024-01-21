from fastapi import APIRouter, Depends
from sqlalchemy import select, and_, Result
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_async_session
from dish.models import Dish
from submenu.models import Submenu

router = APIRouter(prefix="/api/v1/menus", tags=["Dish"])


@router.get("/{target_menu_id}/submenus/{target_submenu_id}/dishes")
async def get_dishes(target_menu_id, target_submenu_id, session: AsyncSession = Depends(get_async_session)) -> list:
    """
    Функция для получения блюд привязанных к подменю.

    Args:
        target_menu_id: идентификатор меню, к которому привязано submenu
        target_submenu_id: идентификатор подменю, к которому привязано блюдо
        session:

    Returns: Список найденных блюд.

    """
    stmt = select(Dish).join(Submenu).where(
        and_(
            Submenu.menu_id == target_menu_id,
            Dish.submenu_id == target_submenu_id
        )
    )

    result: Result = await session.execute(stmt)

    dishes = result.scalars().all()

    return list(dishes)
