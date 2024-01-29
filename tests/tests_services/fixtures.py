"""
Модуль с описанием фикстур, которые позволят пользоваться закешированными данными о созданных записях.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 27 января 2024
"""

import os

import pytest
from httpx import AsyncClient, Response
from .test_data import (
    MENU_TITLE_VALUE_TO_CREATE,
    MENU_DESCRIPTION_VALUE_TO_CREATE,

    SUBMENU_TITLE_VALUE_TO_CREATE,
    SUBMENU_DESCRIPTION_VALUE_TO_CREATE,

    DISH_TITLE_VALUE_TO_CREATE,
    DISH_DESCRIPTION_VALUE_TO_CREATE,
    DISH_PRICE_TO_CREATE,

    SECOND_DISH_TITLE_VALUE_TO_CREATE,
    SECOND_DISH_PRICE_TO_CREATE,
    SECOND_DISH_DESCRIPTION_VALUE_TO_CREATE,
)
from tests_services.services import get_created_object_attribute


@pytest.fixture(scope="session")
async def create_menu_using_post_method_fixture(ac: AsyncClient) -> Response:
    """
    Фикстура, которая используется при создании меню с помощью метода POST и используется в дальнейшем, для получения
    данных из различных эндпоинтов с помощью uuid созданной записи.

    Нужна для получения uuid созданной записи, избежания его повторной генерации, а также для возможности работы с
    одним объектом на протяжении сессии подключения.

    Args:
        ac: клиент для асинхронных HTTP запросов

    Returns:
        Response. Ответ сервера с созданной записью.
    """

    # Создаем меню.
    response = await ac.post(
        url="/api/v1/menus",
        json={
            "title": MENU_TITLE_VALUE_TO_CREATE,
            "description": MENU_DESCRIPTION_VALUE_TO_CREATE,
        },
    )

    # Возвращаем ответ с данными.
    return response


@pytest.fixture(scope="session")
async def create_submenu_using_post_method_fixture(
        ac: AsyncClient, create_menu_using_post_method_fixture: Response
) -> Response:
    """
    Фикстура, которая используется при создании подменю с помощью метода POST и используется в дальнейшем, для получения
    данных из различных эндпоинтов с помощью uuid созданной записи.

    Args:
        ac: клиент для асинхронных HTTP запросов
        create_menu_using_post_method_fixture: фикстура и данными о созданном меню.

    Returns:
        Response. Ответ сервера с созданной записью.
    """

    target_menu_id = os.environ.get("TARGET_MENU_ID")

    # Создаем подменю.
    create_submenu_response = await ac.post(
        url=f"/api/v1/menus/{target_menu_id}/submenus",
        json={
            "title": SUBMENU_TITLE_VALUE_TO_CREATE,
            "description": SUBMENU_DESCRIPTION_VALUE_TO_CREATE,
        },
    )

    # Возвращаем ответ с данными.
    return create_submenu_response


async def create_dish(
        ac: AsyncClient,
        target_menu_id: str,
        target_submenu_id: str,
        title: str,
        description: str,
        price: float,
) -> Response:
    return await ac.post(
        url=f"/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes",
        json={
            "title": title,
            "description": description,
            "price": str(price),
        },
    )


@pytest.fixture(scope="session")
async def create_dish_using_post_method_fixture(
        ac: AsyncClient,
        create_menu_using_post_method_fixture: Response,
        create_submenu_using_post_method_fixture: Response,
) -> Response:
    target_menu_id = os.environ.get("TARGET_MENU_ID")
    target_submenu_id = os.environ.get("TARGET_SUBMENU_ID")

    # Создаем первое блюдо.
    create_dish_response = await create_dish(
        ac,
        target_menu_id,
        target_submenu_id,
        DISH_TITLE_VALUE_TO_CREATE,
        DISH_DESCRIPTION_VALUE_TO_CREATE,
        DISH_PRICE_TO_CREATE,
    )

    # Возвращаем ответ с данными.
    return create_dish_response


@pytest.fixture(scope="session")
async def create_second_dish_using_post_method_fixture(
        ac: AsyncClient,
        create_menu_using_post_method_fixture: Response,
        create_submenu_using_post_method_fixture: Response,
) -> Response:
    target_menu_id = os.environ.get("TARGET_MENU_ID")
    target_submenu_id = os.environ.get("TARGET_SUBMENU_ID")

    # Создаем второе блюдо.
    create_dish_response = await create_dish(
        ac,
        target_menu_id,
        target_submenu_id,
        SECOND_DISH_TITLE_VALUE_TO_CREATE,
        SECOND_DISH_DESCRIPTION_VALUE_TO_CREATE,
        SECOND_DISH_PRICE_TO_CREATE,
    )

    # Возвращаем ответ с данными.
    return create_dish_response
