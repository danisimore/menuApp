"""
Модуль для тестирования CRUD операций, связанных с подменю.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 29 января 2024
"""

import os

import pytest
from httpx import AsyncClient, Response

from tests_services.internal_tests import (
    assert_response,

    get_object_when_table_is_empty_internal_test,
    create_object_internal_test,
    delete_object_internal_test,
    get_objects_when_table_is_not_empty_internal_test,
    get_specific_object_when_table_is_empty_internal_test,
)

from tests_services.services import (
    save_created_object_id,
)

from tests_services.fixtures import (
    create_menu_using_post_method_fixture,
    create_submenu_using_post_method_fixture,
)

from tests_services.test_data import (
    MENU_TITLE_VALUE_TO_CREATE,
    MENU_DESCRIPTION_VALUE_TO_CREATE,
    SUBMENU_TITLE_VALUE_TO_CREATE,
    SUBMENU_DESCRIPTION_VALUE_TO_CREATE,
    SUBMENU_TITLE_VALUE_TO_UPDATE,
    SUBMENU_DESCRIPTION_VALUE_TO_UPDATE,
)


@pytest.mark.asyncio
async def test_create_menu_from_submenu_using_post_method(
    ac: AsyncClient, create_menu_using_post_method_fixture: Response
) -> None:
    """
    Тестирование создания меню в рамках теста CRUD для подменю.

    Тест проходит успешно, если:
        1. Код ответа 201.
        2. title созданной записи, которую вернул сервер, совпадает с переданным title'ом в запросе.
        3. description созданной записи, которую вернул сервер, совпадает с переданным description'ом в запросе.

    Args:
        ac: клиент для асинхронных HTTP запросов.
        create_menu_using_post_method_fixture: фикстура, представляющая собой закешированый ответ сервера на POST
        запрос на создание меню.

    Returns:
        None
    """

    await create_object_internal_test(
        create_object_using_post_method_fixture=create_menu_using_post_method_fixture,
        env_name="TARGET_MENU_ID",
        expected_data={
            "title": MENU_TITLE_VALUE_TO_CREATE,
            "description": MENU_DESCRIPTION_VALUE_TO_CREATE,
        },
    )


@pytest.mark.asyncio
async def test_get_submenus_for_created_menu_method_when_table_is_empty(
    ac: AsyncClient,
) -> None:
    """
    Функция тестирует получение всех подменю для созданного меню когда таблица submenus не содержит ни одной записи для
    этого меню.

    Тест проходит успешно, если:
        1. Код ответа 404.
        2. Тело ответа от сервера == {'detail': 'Not Found'}

    Args:
        ac: клиент для асинхронных HTTP запросов.

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus.
    target_menu_id = os.environ.get("TARGET_MENU_ID")

    response = await ac.get(url=f"/api/v1/menus{target_menu_id}/submenus")

    assert_response(
        response=response,
        expected_status_code=404,
        expected_data={"detail": "Not Found"},
    )


@pytest.mark.asyncio
async def test_create_submenu_using_post_method(
    ac: AsyncClient, create_submenu_using_post_method_fixture: Response
) -> None:
    """
    Тестирование создания подменю, путем отправки POST запроса.

    Тест проходит успешно, если:
        1. Код ответа 201.
        2. Данные из тела ответа соответствуют данным, переданным в запросе. Т.е. сервер вернул данные созданной записи
           и они соответствуют указанным.

    Args:
        ac: клиент для асинхронных HTTP запросов,

        create_submenu_using_post_method_fixture: фикстура, для отправки POST запроса. В дальнейшем будет
        содержать закешированый ответ сервера на POST запрос

    Returns:
        None
    """

    # Получаем id созданного меню, к которому должно быть привязано подменю
    target_menu_id = os.environ.get("TARGET_MENU_ID")

    await create_object_internal_test(
        create_object_using_post_method_fixture=create_submenu_using_post_method_fixture,
        env_name="TARGET_SUBMENU_ID",
        expected_data={
            "title": SUBMENU_TITLE_VALUE_TO_CREATE,
            "description": SUBMENU_DESCRIPTION_VALUE_TO_CREATE,
            "menu_id": target_menu_id,
        },
    )


@pytest.mark.asyncio
async def test_get_submenus_method_when_table_is_not_empty(ac: AsyncClient) -> None:
    """
    Функция тестирует получение всех подменю для созданного меню когда таблица submenus содержит записи для
    этого меню.

        Тест проходит успешно, если:
        1. Код ответа 200.
        2. В теле ответа не пустой список.

    Args:
        ac: клиент для асинхронных HTTP запросов.

    Returns:
        None
    """

    target_menu_id = os.environ.get("TARGET_MENU_ID")

    await get_objects_when_table_is_not_empty_internal_test(
        ac=ac, url=f"/api/v1/menus/{target_menu_id}/submenus"
    )


@pytest.mark.asyncio
async def test_get_specific_submenu_method(ac: AsyncClient) -> None:
    """
    Функция тестирует получение определенного подменю для созданного меню.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. title найденной записи, которую вернул сервер, совпадает title'ом созданной ранее записи.
        3. description найденной записи, которую вернул сервер, совпадает description'ом созданной ранее записи.
        4. menu_id найденной записи, которую вернул сервер, совпадает menu_id созданной ранее записи.
        5. В ответе были данные о блюдах и их количестве

    Args:
        ac: клиент для асинхронных HTTP запросов,

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus.
    target_menu_id = os.environ.get("TARGET_MENU_ID")

    # Получаем uuid, который вернул сервер после создания записи в таблице submenus.
    target_submenu_id = os.environ.get("TARGET_SUBMENU_ID")

    response = await ac.get(
        f"/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}"
    )

    assert_response(
        response=response,
        expected_status_code=200,
        expected_data={
            "id": target_submenu_id,
            "title": SUBMENU_TITLE_VALUE_TO_CREATE,
            "description": SUBMENU_DESCRIPTION_VALUE_TO_CREATE,
            "menu_id": target_menu_id,
            "dishes": [],
            "dishes_count": 0,
        },
    )


@pytest.mark.asyncio
async def test_update_submenu_using_patch_method(ac: AsyncClient) -> None:
    """
    Функция тестирует обновление определенного подменю с помощью отправки запроса с методом PATCH.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. id обновленной записи совпадает с id созданной ранее записи. Т.е. это должна быть одна и та же запись.
        3. title обновленной записи возвращаемой сервером, совпадает title'ом из константы, на которую старый title
           должен быть обновлен.
        4. description обновленной записи возвращаемой сервером, совпадает description'ом из константы, на которую
           старый description должен быть обновлен.

    Args:
        ac: клиент для асинхронных HTTP запросов,

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus.
    target_menu_id = os.environ.get("TARGET_MENU_ID")

    # Получаем uuid, который вернул сервер после создания записи в таблице submenus.
    target_submenu_id = os.environ.get("TARGET_SUBMENU_ID")

    response = await ac.patch(
        url=f"/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}",
        json={
            "title": SUBMENU_TITLE_VALUE_TO_UPDATE,
            "description": SUBMENU_DESCRIPTION_VALUE_TO_UPDATE,
        },
    )

    assert_response(
        response=response,
        expected_status_code=200,
        expected_data={
            "id": target_submenu_id,
            "title": SUBMENU_TITLE_VALUE_TO_UPDATE,
            "description": SUBMENU_DESCRIPTION_VALUE_TO_UPDATE,
            "menu_id": target_menu_id,
        },
    )


@pytest.mark.asyncio
async def test_get_specific_submenu_method_after_update(ac: AsyncClient) -> None:
    """
    Тестирование получения определенной записи из таблицы submenus по переданным параметрам пути в запросе.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. title найденной записи, которую вернул сервер, совпадает title'ом обновленной ранее записи.
        3. description найденной записи, которую вернул сервер, совпадает description'ом обновленной ранее записи.
        4. В ответе были данные о блюдах и их количестве

    Args:
        ac: клиент для асинхронных HTTP запросов,

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus.
    target_menu_id = os.environ.get("TARGET_MENU_ID")

    # Получаем uuid, который вернул сервер после создания записи в таблице submenus.
    target_submenu_id = os.environ.get("TARGET_SUBMENU_ID")

    response = await ac.get(
        url=f"/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}"
    )

    assert_response(
        response=response,
        expected_status_code=200,
        expected_data={
            "id": target_submenu_id,
            "title": SUBMENU_TITLE_VALUE_TO_UPDATE,
            "description": SUBMENU_DESCRIPTION_VALUE_TO_UPDATE,
            "menu_id": target_menu_id,
            "dishes": [],
            "dishes_count": 0,
        },
    )


@pytest.mark.asyncio
async def test_delete_submenu_method(ac: AsyncClient) -> None:
    """
    Тест удаления записи.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. Тело ответа от сервера == {"status": "success!"}

    Args:
        ac: клиент для асинхронных HTTP запросов,

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus.
    target_menu_id = os.environ.get("TARGET_MENU_ID")

    # Получаем uuid, который вернул сервер после создания записи в таблице submenus.
    target_submenu_id = os.environ.get("TARGET_SUBMENU_ID")

    await delete_object_internal_test(
        ac=ac, url=f"/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}"
    )


@pytest.mark.asyncio
async def test_get_submenus_method_after_delete(ac: AsyncClient) -> None:
    """
    Тестирование события получения всех записей из таблицы submenus, когда запись была удалена из таблицы.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. Ответ содержит пустой список

    Args:
        ac: клиент для асинхронных HTTP запросов,

    Returns:
        None
    """

    target_menu_id = os.environ.get("TARGET_MENU_ID")

    url = f"/api/v1/menus/{target_menu_id}/submenus"
    await get_object_when_table_is_empty_internal_test(ac=ac, url=url)


@pytest.mark.asyncio
async def test_get_specific_submenu_method_after_delete(ac: AsyncClient) -> None:
    """
    Тестирование события получения определенной из таблицы submenus, когда запись была удалена из таблицы.

    Тест проходит успешно, если:
        1. Код ответа 404.
        2. Тело ответа от сервера == {"detail": "submenu not found"}

    Args:
        ac: клиент для асинхронных HTTP запросов,

    Returns:
        None
    """

    target_menu_id = os.environ.get("TARGET_MENU_ID")
    target_submenu_id = os.environ.get("TARGET_SUBMENU_ID")

    await get_specific_object_when_table_is_empty_internal_test(
        ac=ac,
        url=f"/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}",
        expected_data={"detail": "submenu not found"},
    )


@pytest.mark.asyncio
async def test_delete_menu_from_submenu_method(ac: AsyncClient) -> None:
    """
    Тестирование удаления меню путем отправки запроса с методом DELETE.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. Тело ответа от сервера == {"status": "success!"}

    Args:
        ac: клиент для асинхронных HTTP запросов,

    Returns:
        None
    """

    target_menu_id = os.environ.get("TARGET_MENU_ID")

    await delete_object_internal_test(ac=ac, url=f"/api/v1/menus/{target_menu_id}")


@pytest.mark.asyncio
async def test_get_menus_after_delete_from_submenu_method(ac: AsyncClient) -> None:
    """
    Тестирование получения меню после удаления.

    Тест проходит успешно, если:
        1. Код ответа 200;
        2. В теле ответа - пустой список.

    Args:
        ac: клиент для асинхронных HTTP запросов,

    Returns:
        None
    """

    url = "/api/v1/menus"

    await get_object_when_table_is_empty_internal_test(ac=ac, url=url)
