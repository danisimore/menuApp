from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_async_session
from .schemas import MenuCreate
from .models import Menu
from .utils import get_created_object_dict

router = APIRouter(
    prefix="/api/v1",
    tags=["Menu"]
)


@router.get("/menus")
async def get_all_menus(session: AsyncSession = Depends(get_async_session)):
    query = select(Menu)
    result = await session.execute(query)

    return result.scalars().all()


@router.get("/menus/{target_menu_id}")
async def get_specific_menu(target_menu_id, session: AsyncSession = Depends(get_async_session)):
    """

    Args:
        target_menu_id: идентификатор записи, данные о которой необходимо получить;
        session: сессия подключения к БД.

    Returns: Menu. Объект найденной по id записи.

    """
    print(type(Menu))
    query = select(Menu).where(Menu.id == target_menu_id)
    result = await session.execute(query)

    return result.scalars().all()[0]


@router.post("/menus")
async def create_menu(new_menu_data: MenuCreate, session: AsyncSession = Depends(get_async_session)) -> JSONResponse:
    """
    Функция для обработки POST запроса.

    Args:
        new_menu_data: данные для создания новой записи в таблице menu;
        session: сессия подключения к БД.

    Returns: JSONResponse.

    """

    # Генерируем SQL код для того, чтобы внести данные в таблицу menu и вернуть их.
    stmt = insert(Menu).values(**new_menu_data.model_dump()).returning(Menu)
    # Исполняем SQL код.
    result = await session.execute(stmt)
    # Получаем объект записи, созданной в БД.
    created_menu = result.scalars().all()[0]

    # Формируем словарь на основе данных о созданном объекте.
    created_menu_dict = get_created_object_dict(created_object=created_menu)

    await session.commit()

    return JSONResponse(content=created_menu_dict, status_code=201)
