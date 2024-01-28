"""
Модуль для тестирования CRUD операций, связанных с меню.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 27 января 2024
"""
import os

import pytest
from httpx import AsyncClient, Response

from tests_services.services import (
    assert_response,
    get_created_object_attribute,
    save_created_object_id,
    test_get_menus_when_table_is_empty
)
from tests_services.test_data import (
    MENU_TITLE_VALUE_TO_CREATE,
    MENU_TITLE_VALUE_TO_UPDATE,
    MENU_DESCRIPTION_VALUE_TO_CREATE,
    MENU_DESCRIPTION_VALUE_TO_UPDATE,
)
from tests_services.fixtures import create_menu_using_post_method_fixture


@pytest.mark.asyncio
async def test_get_menus_method_when_table_is_empty(ac: AsyncClient) -> None:
    """
    Тестирование события получения всех записей из таблицы menus, когда в таблице еще нет ни одной записи.

    Тест проходит успешно, если:
        1. Код ответа 200;
        2. В теле ответа - пустой список.

    Args:
        ac: клиент для асинхронных HTTP запросов.

    Returns:
        None
    """

    await test_get_menus_when_table_is_empty(ac=ac)


@pytest.mark.asyncio
async def test_create_menu_using_post_method(
        ac: AsyncClient, create_menu_using_post_method_fixture: Response
) -> None:
    """
    Тестирование создания меню, путем отправки POST запроса.

    Тест проходит успешно, если:
        1. Код ответа 201.
        2. title созданной записи, которую вернул сервер, совпадает с переданным title'ом в запросе.
        3. description созданной записи, которую вернул сервер, совпадает с переданным description'ом в запросе.

    Args:
        ac: клиент для асинхронных HTTP запросов.
        create_menu_using_post_method_fixture: фикстура, для отправки POST запроса и сохранения ответа сервера в кеше

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus.
    target_menu_id = save_created_object_id(create_menu_using_post_method_fixture, env_name="TARGET_MENU_ID")

    assert_response(
        response=create_menu_using_post_method_fixture,
        expected_status_code=201,
        expected_data={
            "id": target_menu_id,
            "title": MENU_TITLE_VALUE_TO_CREATE,
            "description": MENU_DESCRIPTION_VALUE_TO_CREATE,
        }
    )


@pytest.mark.asyncio
async def test_get_menus_method_when_table_is_not_empty(ac: AsyncClient) -> None:
    """
    Тестирование события получения всех записей из таблицы menus, когда в таблице есть записи.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. Ответ содержит не пустой список.

    Args:
        ac: клиент для асинхронных HTTP запросов.

    Returns:
        None
    """
    response = await ac.get(url="/api/v1/menus")

    assert response.status_code == 200 and len(response.json()) != 0


@pytest.mark.asyncio
async def test_get_specific_menu_method(ac: AsyncClient) -> None:
    """
    Тестирование получения определенной записи из таблицы menus по переданному параметру пути в запросе.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. title найденной записи, которую вернул сервер, совпадает title'ом созданной ранее записи.
        3. description найденной записи, которую вернул сервер, совпадает description'ом созданной ранее записи.
        4. В ответе были данные о подменю, количестве подменю, а также количестве блюд, связанных с меню через все
           подменю.

    Args:
        ac: клиент для асинхронных HTTP запросов.

    Returns:
        None
    """

    target_menu_id = os.environ.get("TARGET_MENU_ID")
    # Сохраняем ответ сервера, делая запрос с параметром uuid.
    response = await ac.get(url=f"/api/v1/menus/{target_menu_id}")

    assert_response(
        response=response,
        expected_status_code=200,
        expected_data={
            "id": target_menu_id,
            "title": MENU_TITLE_VALUE_TO_CREATE,
            "description": MENU_DESCRIPTION_VALUE_TO_CREATE,
            "submenus": [],
            "submenus_count": 0,
            "dishes_count": 0,
        }
    )


@pytest.mark.asyncio
async def test_update_menu_using_patch_method(ac: AsyncClient) -> None:
    """
    Тестирование обновления записи с помощью отправки запроса с методом PATCH

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. id обновленной записи совпадает с id созданной ранее записи. Т.е. это должна быть одна и та же запись.
        3. title обновленной записи возвращаемой сервером, совпадает title'ом из константы, на которую старый title
           должен быть обновлен.
        4. description обновленной записи возвращаемой сервером, совпадает description'ом из константы, на которую
           старый description должен быть обновлен.

    Args:
        ac: клиент для асинхронных HTTP запросов.

    Returns:
        None
    """

    target_menu_id = os.environ.get("TARGET_MENU_ID")

    response = await ac.patch(
        url=f"/api/v1/menus/{target_menu_id}",
        json={
            "title": MENU_TITLE_VALUE_TO_UPDATE,
            "description": MENU_DESCRIPTION_VALUE_TO_UPDATE,
        },
    )

    assert_response(
        response=response,
        expected_status_code=200,
        expected_data={
            "id": target_menu_id,
            "title": MENU_TITLE_VALUE_TO_UPDATE,
            "description": MENU_DESCRIPTION_VALUE_TO_UPDATE,
        }
    )


@pytest.mark.asyncio
async def test_get_specific_menu_method_after_update(ac: AsyncClient) -> None:
    """
    Тестирование получения определенной записи из таблицы menus по переданному параметру пути в запросе.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. title найденной записи, которую вернул сервер, совпадает title'ом обновленной ранее записи.
        3. description найденной записи, которую вернул сервер, совпадает description'ом обновленной ранее записи.
        4. В ответе были данные о подменю, количестве подменю, а также количестве блюд, связанных с меню через все
           подменю.

    Args:
        ac: клиент для асинхронных HTTP запросов,

    Returns:
        None
    """

    target_menu_id = os.environ.get("TARGET_MENU_ID")

    # Сохраняем ответ сервера, делая запрос с параметром uuid.
    response = await ac.get(url=f"/api/v1/menus/{target_menu_id}")

    assert_response(
        response=response,
        expected_status_code=200,
        expected_data={
            "id": target_menu_id,
            "title": MENU_TITLE_VALUE_TO_UPDATE,
            "description": MENU_DESCRIPTION_VALUE_TO_UPDATE,
            "submenus": [],
            "submenus_count": 0,
            "dishes_count": 0,
        }
    )


@pytest.mark.asyncio
async def test_delete_menu_method(ac: AsyncClient) -> None:
    """
    Тест удаления записи.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. Тело ответа от сервера == {"status": "success!"}

    Args:
        ac: клиент для асинхронных HTTP запросов.

    Returns:
        None
    """

    target_menu_id = os.environ.get("TARGET_MENU_ID")

    # Делаем запрос с методом DELETE.
    response = await ac.delete(url=f"/api/v1/menus/{target_menu_id}")

    assert_response(
        response=response,
        expected_status_code=200,
        expected_data={"status": "success!"}
    )


@pytest.mark.asyncio
async def test_get_menus_method_after_delete(ac: AsyncClient) -> None:
    """
    Тестирование события получения всех записей из таблицы menus, когда запись была удалена из таблицы.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. Ответ содержит пустой список.

    Args:
        ac: клиент для асинхронных HTTP запросов.

    Returns:
        None
    """

    await test_get_menus_when_table_is_empty(ac=ac)


@pytest.mark.asyncio
async def test_get_specific_menu_method_after_delete(ac: AsyncClient) -> None:
    """
    Тестирование получения определенного меню по id, которого не существует в БД.

    Тест проходит успешно, если:
        1. Код ответа 404.
        2. Тело ответа от сервера == {"detail": "menu not found"}

    Args:
        ac: клиент для асинхронных HTTP запросов.

    Returns:
        None
    """

    target_menu_id = os.environ.get("TARGET_MENU_ID")

    # Сохраняем ответ сервера, делая запрос с параметром uuid.
    response = await ac.get(url=f"/api/v1/menus/{target_menu_id}")

    assert_response(
        response=response,
        expected_status_code=404,
        expected_data={"detail": "menu not found"}
    )
