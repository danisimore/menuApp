from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import insert, select, Result, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_async_session
from .schemas import MenuCreate, MenuUpdate
from .models import Menu
from .utils import get_created_object_dict

router = APIRouter(
    prefix="/api/v1",
    tags=["Menu"]
)


@router.get("/menus")
async def get_all_menus(session: AsyncSession = Depends(get_async_session)):
    stmt = select(Menu)
    result: Result = await session.execute(stmt)

    menus = result.scalars().all()

    return menus


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

    # Делаем коммит для завершения транзакции.
    await session.commit()

    return JSONResponse(content=created_menu_dict, status_code=201)


@router.get("/menus/{target_menu_id}")
async def get_specific_menu(target_menu_id, session: AsyncSession = Depends(get_async_session)):
    """
    Функция для вывода меню по заданному id

    Args:
        target_menu_id: идентификатор записи, данные о которой необходимо получить;
        session: сессия подключения к БД.

    Returns: Объект найденной по id записи.

    """

    return await session.get(Menu, target_menu_id)


@router.patch("/menus/{target_menu_id}")
async def update_specific_menu(
        target_menu_id,
        update_menu_data: MenuUpdate,
        session: AsyncSession = Depends(get_async_session)
) -> JSONResponse:
    """
    Функция для обработки запроса с методом PATCH.

    Args:
        target_menu_id: id записи, которую необходимо обновить
        update_menu_data: данные, на которые будут заменены текущие
        session: сессия подключения к БД.

    Returns: JSONResponse, который содержит объект обновленной записи и статус код.

    """

    # Генерируем SQL код для того, чтобы обновить данные записи и вернуть их.
    stmt = update(Menu).values(**update_menu_data.model_dump()).where(Menu.id == target_menu_id).returning(Menu)

    # Исполняем SQL код.
    result = await session.execute(stmt)

    # Получаем объект созданной записи.
    updated_menu = result.scalars().all()[0]

    # Формируем словарь на основе этого объекта.
    updated_menu_dict = get_created_object_dict(created_object=updated_menu)

    # Делаем коммит для завершения транзакции.
    await session.commit()

    return JSONResponse(content=updated_menu_dict, status_code=200)
