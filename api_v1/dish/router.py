from fastapi import APIRouter, Depends
from sqlalchemy import select, and_, Result, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from database.database import get_async_session
from dish.models import Dish
from dish.schemas import CreateDish, UpdateDish
from dish.services import is_submenu_in_target_menu
from menu.utils import get_created_object_dict
from submenu.models import Submenu
from dish.utils import format_decimal

router = APIRouter(prefix="/api/v1/menus", tags=["Dish"])


@router.get("/{target_menu_id}/submenus/{target_submenu_id}/dishes")
async def get_dishes(
        target_menu_id: str,
        target_submenu_id: str,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Функция для получения блюд привязанных к подменю.

    Args:
        target_menu_id: идентификатор меню, к которому привязано submenu
        target_submenu_id: идентификатор подменю, к которому привязано блюдо
        session:

    Returns: Список найденных блюд.

    """

    stmt = (
        select(Dish)
        .join(Submenu)
        .where(
            and_(
                Submenu.menu_id == target_menu_id, Dish.submenu_id == target_submenu_id
            )
        )
    )

    result: Result = await session.execute(stmt)

    dishes = result.scalars().all()

    return dishes


@router.post("/{target_menu_id}/submenus/{target_submenu_id}/dishes")
async def create_dish(
        target_menu_id: str,
        target_submenu_id: str,
        dish_data: CreateDish,
        session: AsyncSession = Depends(get_async_session),
):
    submenu_in_target_menu = await is_submenu_in_target_menu(
        submenu=Submenu,
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
        session=session,
    )

    if not submenu_in_target_menu:
        return JSONResponse(
            content={
                "detail": "the menu object with the identifier you passed has no connection with "
                          "the submenu object whose identifier you passed"
            },
            status_code=404,
        )

    dish_data_dict = dish_data.model_dump()
    dish_data_dict["submenu_id"] = target_submenu_id
    print(type(dish_data_dict["price"]))
    stmt = insert(Dish).values(dish_data_dict).returning(Dish)

    result = await session.execute(stmt)

    created_dish = result.scalars().all()[0]

    created_dish_dict = get_created_object_dict(created_object=created_dish)

    await session.commit()

    return JSONResponse(content=created_dish_dict, status_code=201)


@router.get("/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}")
async def get_specific_dish(
        target_menu_id: str,
        target_submenu_id: str,
        target_dish_id: str,
        session: AsyncSession = Depends(get_async_session),
):
    stmt = (
        select(Dish)
        .join(Submenu)
        .where(
            and_(
                Submenu.menu_id == target_menu_id, Dish.submenu_id == target_submenu_id, Dish.id == target_dish_id
            )
        )
    )

    result = await session.execute(stmt)

    try:
        dish = result.scalars().all()[0]
    except IndexError:
        return JSONResponse(content={"detail": "dish not found"}, status_code=404)

    dish_dict = {
        "id": str(dish.id),
        "title": dish.title,
        "description": dish.description,
        "price": format_decimal(dish.price),
        "submenu_id": str(dish.submenu_id),
    }

    return JSONResponse(content=dish_dict)


@router.patch("/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}")
async def update_dish(
        target_menu_id: str,
        target_submenu_id: str,
        target_dish_id: str,
        dish_data: UpdateDish,
        session: AsyncSession = Depends(get_async_session),
):
    submenu_in_target_menu = await is_submenu_in_target_menu(
        submenu=Submenu,
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
        session=session,
    )

    if not submenu_in_target_menu:
        return JSONResponse(
            content={
                "detail": "the menu object with the identifier you passed has no connection with "
                          "the submenu object whose identifier you passed"
            },
            status_code=404,
        )

    stmt = (
        update(Dish)
        .where(
            and_(
                Dish.submenu_id == target_submenu_id, Dish.id == target_dish_id
            )
        )
        .values(**dish_data.model_dump())
    ).returning(Dish)

    result = await session.execute(stmt)

    updated_dish = result.scalars().all()[0]

    updated_dish_dict = get_created_object_dict(updated_dish)

    await session.commit()

    return JSONResponse(content=updated_dish_dict, status_code=200)


@router.delete("/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}")
async def delete_dish(
        target_menu_id: str,
        target_submenu_id: str,
        target_dish_id: str,
        session: AsyncSession = Depends(get_async_session),
):
    submenu_in_target_menu = await is_submenu_in_target_menu(
        submenu=Submenu,
        target_menu_id=target_menu_id,
        target_submenu_id=target_submenu_id,
        session=session,
    )

    if not submenu_in_target_menu:
        return JSONResponse(
            content={
                "detail": "the menu object with the identifier you passed has no connection with "
                          "the submenu object whose identifier you passed"
            },
            status_code=404,
        )

    stmt = delete(Dish).where(and_(Dish.submenu_id == target_submenu_id, Dish.id == target_dish_id))

    await session.execute(stmt)

    await session.commit()

    return JSONResponse(content={"status": "Success!"}, status_code=200)
