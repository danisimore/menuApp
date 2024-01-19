from fastapi import APIRouter, Depends
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from .schemas import MenuCreate
from .models import Menu

router = APIRouter(
    prefix="/menu",
    tags=["Menu"]
)


@router.get("/get")
async def get_all_menus(session: AsyncSession = Depends(get_async_session)):
    query = select(Menu)
    result = await session.execute(query)

    return result.scalars().all()


@router.post("/create")
async def create_menu(new_menu_data: MenuCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(Menu).values(**new_menu_data.model_dump())
    await session.execute(stmt)
    await session.commit()
    return {"status": "Success!"}
