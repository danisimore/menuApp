"""
Модуль для тестирования CRUD операций, связанных с блюдами.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 30 января 2024 | Избавился от общих переменных.
"""

import os
import pytest
from httpx import AsyncClient, Response

from tests_services.fixtures import (
    create_menu_using_post_method_fixture,
    create_submenu_using_post_method_fixture,
    create_dish_using_post_method_fixture,
)

from tests_services.services import get_created_object_attribute

from tests_services.internal_tests import (
    assert_response,

    get_object_when_table_is_empty_internal_test,
    create_object_internal_test,
    delete_object_internal_test,
    get_objects_when_table_is_not_empty_internal_test,
    get_specific_object_when_table_is_empty_internal_test,
)

from tests_services.test_data import (
    MENU_TITLE_VALUE_TO_CREATE,
    MENU_DESCRIPTION_VALUE_TO_CREATE,

    SUBMENU_TITLE_VALUE_TO_CREATE,
    SUBMENU_DESCRIPTION_VALUE_TO_CREATE,
    DISH_TITLE_VALUE_TO_CREATE,
    DISH_DESCRIPTION_VALUE_TO_CREATE,
    DISH_PRICE_TO_CREATE,
    DISH_TITLE_VALUE_TO_UPDATE,
    DISH_DESCRIPTION_VALUE_TO_UPDATE,
    DISH_PRICE_TO_UPDATE,
)


@pytest.mark.asyncio
async def test_create_menu_from_dish_using_post_method(
        ac: AsyncClient, create_menu_using_post_method_fixture: Response
) -> None:
    """
    Тестирование создания меню в рамках теста CRUD для блюд.

    Тест проходит успешно, если:
        1. Код ответа 201.
        2. title созданной записи, которую вернул сервер, совпадает с переданным title'ом в запросе.
        3. description созданной записи, которую вернул сервер, совпадает с переданным description'ом в запросе.

    Args:
        ac: клиент для асинхронных HTTP запросов.
        create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню

    Returns:
        None
    """

    await create_object_internal_test(
        create_object_using_post_method_fixture=create_menu_using_post_method_fixture,
        expected_data={
            "title": MENU_TITLE_VALUE_TO_CREATE,
            "description": MENU_DESCRIPTION_VALUE_TO_CREATE,
        },
    )


@pytest.mark.asyncio
async def test_create_submenu_from_dish_using_post_method(
        ac: AsyncClient,
        create_submenu_using_post_method_fixture: Response,
        create_menu_using_post_method_fixture: Response
) -> None:
    """
    Тестирование создания подменю в рамках теста CRUD для блюд.

    Тест проходит успешно, если:
        1. Код ответа 201.
        2. Данные из тела ответа соответствуют данным, переданным в запросе. Т.е. сервер вернул данные созданной записи
           и они соответствуют указанным.

    Args:
        ac: клиент для асинхронных HTTP запросов,

        create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,

        create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,

    Returns:
        None
    """

    # Получаем id созданного меню, к которому должно быть привязано подменю
    target_menu_id = get_created_object_attribute(response=create_menu_using_post_method_fixture, attribute="id")

    await create_object_internal_test(
        create_object_using_post_method_fixture=create_submenu_using_post_method_fixture,
        expected_data={
            "title": SUBMENU_TITLE_VALUE_TO_CREATE,
            "description": SUBMENU_DESCRIPTION_VALUE_TO_CREATE,
            "menu_id": target_menu_id,
        },
    )


@pytest.mark.asyncio
async def test_get_dishes_method_when_table_is_empty(
        ac: AsyncClient,
        create_menu_using_post_method_fixture: Response,
        create_submenu_using_post_method_fixture: Response
) -> None:
    """
    Функция тестирует получение всех блюд для созданного подменю когда таблица dishes не содержит ни одной записи для
    этого подменю.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. Тело ответа от сервера - пустой список

    Args:
        ac: клиент для асинхронных HTTP запросов.
        create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,
        create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
    target_menu_id = get_created_object_attribute(response=create_menu_using_post_method_fixture, attribute="id")

    # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
    target_submenu_id = get_created_object_attribute(response=create_submenu_using_post_method_fixture, attribute="id")

    response = await ac.get(
        url=f"/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes"
    )

    assert_response(response=response, expected_status_code=200, expected_data=[])


@pytest.mark.asyncio
async def test_create_dish_using_post_method(
        ac: AsyncClient,
        create_submenu_using_post_method_fixture: Response,
        create_dish_using_post_method_fixture: Response
) -> None:
    """
    Тестирование создания блюда, путем отправки POST запроса.

    Args:
        ac: клиент для асинхронных HTTP запросов.
        create_dish_using_post_method_fixture: фикстура, представляющая собой закешированый ответ сервера на POST
        запрос на создание блюда.

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
    target_submenu_id = get_created_object_attribute(response=create_submenu_using_post_method_fixture, attribute="id")

    await create_object_internal_test(
        create_object_using_post_method_fixture=create_dish_using_post_method_fixture,
        expected_data={
            "title": DISH_TITLE_VALUE_TO_CREATE,
            "description": DISH_DESCRIPTION_VALUE_TO_CREATE,
            "price": str(DISH_PRICE_TO_CREATE),
            "submenu_id": target_submenu_id,
        },
    )


@pytest.mark.asyncio
async def test_get_dishes_method_when_table_is_not_empty(
        ac: AsyncClient,
        create_menu_using_post_method_fixture: Response,
        create_submenu_using_post_method_fixture: Response
) -> None:
    """
    Функция тестирует получение всех блюд для созданного подменю когда таблица dishes содержит записи для
    этого подменю.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. В теле ответа не пустой список.

    Args:
        ac: клиент для асинхронных HTTP запросов.
        create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,
        create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
    target_menu_id = get_created_object_attribute(response=create_menu_using_post_method_fixture, attribute="id")

    # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
    target_submenu_id = get_created_object_attribute(response=create_submenu_using_post_method_fixture, attribute="id")

    await get_objects_when_table_is_not_empty_internal_test(
        ac=ac, url=f"/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes"
    )


@pytest.mark.asyncio
async def test_get_specific_dish_method(
        ac: AsyncClient,
        create_menu_using_post_method_fixture: Response,
        create_submenu_using_post_method_fixture: Response,
        create_dish_using_post_method_fixture: Response
) -> None:
    """
    Функция тестирует получение определенного блюда для созданного подменю.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. title найденной записи, которую вернул сервер, совпадает title'ом созданной ранее записи.
        3. description найденной записи, которую вернул сервер, совпадает description'ом созданной ранее записи.
        4. price найденной записи, которую вернул сервер, совпадает price'ом созданной ранее записи.
        5. submenu_id найденной записи, которую вернул сервер, совпадает menu_id созданной ранее записи.

    Args:
        ac: клиент для асинхронных HTTP запросов,
        create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,
        create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,
        create_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание блюда,

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
    target_menu_id = get_created_object_attribute(response=create_menu_using_post_method_fixture, attribute="id")

    # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
    target_submenu_id = get_created_object_attribute(response=create_submenu_using_post_method_fixture, attribute="id")

    # Получаем uuid, который вернул сервер после создания записи в таблице dishes с помощью фикстуры.
    target_dish_id = get_created_object_attribute(response=create_dish_using_post_method_fixture, attribute="id")

    response = await ac.get(
        url=f"/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}"
    )

    assert_response(
        response=response,
        expected_status_code=200,
        expected_data={
            "id": target_dish_id,
            "title": DISH_TITLE_VALUE_TO_CREATE,
            "description": DISH_DESCRIPTION_VALUE_TO_CREATE,
            "price": str(DISH_PRICE_TO_CREATE),
            "submenu_id": target_submenu_id,
        },
    )


@pytest.mark.asyncio
async def test_update_dish_using_patch_method(
        ac: AsyncClient,
        create_menu_using_post_method_fixture: Response,
        create_submenu_using_post_method_fixture: Response,
        create_dish_using_post_method_fixture: Response
) -> None:
    """
    Функция тестирует обновление определенного блюда с помощью отправки запроса с методом PATCH.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. id обновленной записи совпадает с id созданной ранее записи. Т.е. это должна быть одна и та же запись.
        3. title обновленной записи возвращаемой сервером, совпадает title'ом из константы, на которую старый title
           должен быть обновлен.
        4. description обновленной записи возвращаемой сервером, совпадает description'ом из константы, на которую
           старый description должен быть обновлен.
        5. price обновленной записи возвращаемой сервером, совпадает price'ом из константы, на которую
           старый price должен быть обновлен.
        6. submenu_id обновленной записи возвращаемой сервером, совпадает submenu_id из константы, на которую
           старый submenu_id должен быть обновлен.

    Args:
        ac: клиент для асинхронных HTTP запросов,
        create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,
        create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,
        create_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание блюда,

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
    target_menu_id = get_created_object_attribute(response=create_menu_using_post_method_fixture, attribute="id")

    # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
    target_submenu_id = get_created_object_attribute(response=create_submenu_using_post_method_fixture, attribute="id")

    # Получаем uuid, который вернул сервер после создания записи в таблице dishes с помощью фикстуры.
    target_dish_id = get_created_object_attribute(response=create_dish_using_post_method_fixture, attribute="id")

    response = await ac.patch(
        url=f"/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}",
        json={
            "title": DISH_TITLE_VALUE_TO_UPDATE,
            "description": DISH_DESCRIPTION_VALUE_TO_UPDATE,
            "price": str(DISH_PRICE_TO_UPDATE),
        },
    )

    assert_response(
        response=response,
        expected_status_code=200,
        expected_data={
            "id": target_dish_id,
            "title": DISH_TITLE_VALUE_TO_UPDATE,
            "description": DISH_DESCRIPTION_VALUE_TO_UPDATE,
            "price": str(DISH_PRICE_TO_UPDATE),
            "submenu_id": target_submenu_id,
        },
    )


@pytest.mark.asyncio
async def test_get_specific_dish_method_after_update(
        ac: AsyncClient,
        create_menu_using_post_method_fixture: Response,
        create_submenu_using_post_method_fixture: Response,
        create_dish_using_post_method_fixture: Response
) -> None:
    """
    Тестирование получения определенной записи из таблицы dishes по переданным параметрам пути запроса после обновления.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. title найденной записи, которую вернул сервер, совпадает title'ом обновленной ранее записи.
        3. description найденной записи, которую вернул сервер, совпадает description'ом обновленной ранее записи.
        4. price найденной записи, которую вернул сервер, совпадает price'ом обновленной ранее записи.
        5. submenu_id найденной записи, которую вернул сервер, совпадает submenu_id обновленной ранее записи.

    Args:
        ac: клиент для асинхронных HTTP запросов,
        create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,
        create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,
        create_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание блюда,

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
    target_menu_id = get_created_object_attribute(response=create_menu_using_post_method_fixture, attribute="id")

    # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
    target_submenu_id = get_created_object_attribute(response=create_submenu_using_post_method_fixture, attribute="id")

    # Получаем uuid, который вернул сервер после создания записи в таблице dishes с помощью фикстуры.
    target_dish_id = get_created_object_attribute(response=create_dish_using_post_method_fixture, attribute="id")

    response = await ac.get(
        url=f"/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}"
    )

    assert_response(
        response=response,
        expected_status_code=200,
        expected_data={
            "id": target_dish_id,
            "title": DISH_TITLE_VALUE_TO_UPDATE,
            "description": DISH_DESCRIPTION_VALUE_TO_UPDATE,
            "price": str(DISH_PRICE_TO_UPDATE),
            "submenu_id": target_submenu_id,
        },
    )


@pytest.mark.asyncio
async def test_delete_dish_method(
        ac: AsyncClient,
        create_menu_using_post_method_fixture: Response,
        create_submenu_using_post_method_fixture: Response,
        create_dish_using_post_method_fixture: Response
) -> None:
    """
    Тест удаления записи.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. Тело ответа от сервера == {"status": "success!"}

    Args:
        ac: клиент для асинхронных HTTP запросов,
        create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,
        create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,
        create_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание блюда,

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
    target_menu_id = get_created_object_attribute(response=create_menu_using_post_method_fixture, attribute="id")

    # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
    target_submenu_id = get_created_object_attribute(response=create_submenu_using_post_method_fixture, attribute="id")

    # Получаем uuid, который вернул сервер после создания записи в таблице dishes с помощью фикстуры.
    target_dish_id = get_created_object_attribute(response=create_dish_using_post_method_fixture, attribute="id")

    await delete_object_internal_test(
        ac=ac,
        url=f"/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}",
    )


@pytest.mark.asyncio
async def test_get_dishes_method_after_delete(
        ac: AsyncClient,
        create_menu_using_post_method_fixture: Response,
        create_submenu_using_post_method_fixture: Response,
) -> None:
    """
    Тестирование события получения всех записей из таблицы dishes, когда запись была удалена из таблицы.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. Ответ содержит пустой список

    Args:
        ac: клиент для асинхронных HTTP запросов,
        create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,
        create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
    target_menu_id = get_created_object_attribute(response=create_menu_using_post_method_fixture, attribute="id")

    # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
    target_submenu_id = get_created_object_attribute(response=create_submenu_using_post_method_fixture, attribute="id")

    url = f"/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes"

    await get_object_when_table_is_empty_internal_test(ac=ac, url=url)


@pytest.mark.asyncio
async def test_get_specific_dish_method_after_delete(
        ac: AsyncClient,
        create_menu_using_post_method_fixture: Response,
        create_submenu_using_post_method_fixture: Response,
        create_dish_using_post_method_fixture: Response
) -> None:
    """
    Тестирование события получения определенной из таблицы dishes, когда запись была удалена из таблицы.

    Тест проходит успешно, если:
        1. Код ответа 404.
        2. Тело ответа от сервера == {"detail": "dish not found"}

    Args:
        ac: клиент для асинхронных HTTP запросов,
        create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,
        create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,
        create_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание блюда,

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
    target_menu_id = get_created_object_attribute(response=create_menu_using_post_method_fixture, attribute="id")

    # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
    target_submenu_id = get_created_object_attribute(response=create_submenu_using_post_method_fixture, attribute="id")

    # Получаем uuid, который вернул сервер после создания записи в таблице dishes с помощью фикстуры.
    target_dish_id = get_created_object_attribute(response=create_dish_using_post_method_fixture, attribute="id")

    await get_specific_object_when_table_is_empty_internal_test(
        ac=ac,
        url=f"/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}/dishes/{target_dish_id}",
        expected_data={"detail": "dish not found"},
    )


@pytest.mark.asyncio
async def test_delete_submenu_from_dish_method(
        ac: AsyncClient,
        create_menu_using_post_method_fixture: Response,
        create_submenu_using_post_method_fixture: Response,
) -> None:
    """
    Тестирование удаления подменю путем отправки запроса с методом DELETE.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. Тело ответа от сервера == {"status": "success!"}

    Args:
        ac: клиент для асинхронных HTTP запросов,
        create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,
        create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
    target_menu_id = get_created_object_attribute(response=create_menu_using_post_method_fixture, attribute="id")

    # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
    target_submenu_id = get_created_object_attribute(response=create_submenu_using_post_method_fixture, attribute="id")

    await delete_object_internal_test(
        ac=ac, url=f"/api/v1/menus/{target_menu_id}/submenus/{target_submenu_id}"
    )


@pytest.mark.asyncio
async def test_get_submenus_after_delete_from_dish_method(
        ac: AsyncClient,
        create_menu_using_post_method_fixture: Response
) -> None:
    """
    Тестирование получения подменю после удаления.

    Тест проходит успешно, если:
        1. Код ответа 404.
        2. Тело ответа от сервера == {'detail': 'Not Found'}

    Args:
        ac: клиент для асинхронных HTTP запросов,
        create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
    target_menu_id = get_created_object_attribute(response=create_menu_using_post_method_fixture, attribute="id")

    response = await ac.get(url=f"/api/v1/menus{target_menu_id}/submenus")

    assert_response(
        response=response,
        expected_status_code=404,
        expected_data={"detail": "Not Found"},
    )


@pytest.mark.asyncio
async def test_delete_menu_from_dish_method(
        ac: AsyncClient,
        create_menu_using_post_method_fixture: Response
) -> None:
    """
    Тестирование удаления меню путем отправки запроса с методом DELETE.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. Тело ответа от сервера == {"status": "success!"}

    Args:
        ac: клиент для асинхронных HTTP запросов,
        create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
    target_menu_id = get_created_object_attribute(response=create_menu_using_post_method_fixture, attribute="id")

    await delete_object_internal_test(ac=ac, url=f"/api/v1/menus/{target_menu_id}")


@pytest.mark.asyncio
async def test_get_menus_after_delete_from_dish_method(ac: AsyncClient) -> None:
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
