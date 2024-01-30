"""
Модуль для тестирования сценария проверки кол-ва блюд и подменю в меню.

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
    create_second_dish_using_post_method_fixture
)

from tests_services.internal_tests import (
    assert_response,

    create_object_internal_test,
    delete_object_internal_test,
    get_object_when_table_is_empty_internal_test
)

from tests_services.services import get_created_object_attribute

from tests_services.test_data import (
    MENU_TITLE_VALUE_TO_CREATE,
    MENU_DESCRIPTION_VALUE_TO_CREATE,

    SUBMENU_TITLE_VALUE_TO_CREATE,
    SUBMENU_DESCRIPTION_VALUE_TO_CREATE,

    DISH_TITLE_VALUE_TO_CREATE,
    DISH_DESCRIPTION_VALUE_TO_CREATE,
    DISH_PRICE_TO_CREATE,

    SECOND_DISH_TITLE_VALUE_TO_CREATE,
    SECOND_DISH_DESCRIPTION_VALUE_TO_CREATE,
    SECOND_DISH_PRICE_TO_CREATE
)


@pytest.mark.asyncio
async def test_create_menu_from_check_quan_of_dishes_and_submenus_using_post_method(
        ac: AsyncClient, create_menu_using_post_method_fixture: Response
) -> None:
    """
    Тестирование создания меню в рамках теста проверки количества блюд и подменю в меню.

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
        expected_data={
            "title": MENU_TITLE_VALUE_TO_CREATE,
            "description": MENU_DESCRIPTION_VALUE_TO_CREATE,
        },
    )


@pytest.mark.asyncio
async def test_create_submenu_from_check_quan_of_dishes_and_submenus_using_post_method(
        ac: AsyncClient,
        create_submenu_using_post_method_fixture: Response,
        create_menu_using_post_method_fixture: Response
) -> None:
    """
    Тестирование создания подменю в рамках теста проверки количества блюд и подменю в меню.

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

    # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
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
async def test_create_first_dish_from_check_quan_of_dishes_and_submenus_using_post_method(
        ac: AsyncClient,
        create_dish_using_post_method_fixture: Response,
        create_submenu_using_post_method_fixture: Response
) -> None:
    """
    Тестирование создания первого блюда в рамках теста проверки количества блюд и подменю в меню.

    Args:
        ac: клиент для асинхронных HTTP запросов,
        create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,
        create_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание блюда,

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
async def test_create_second_dish_from_check_quan_of_dishes_and_submenus_using_post_method(
        ac: AsyncClient,
        create_second_dish_using_post_method_fixture: Response,
        create_submenu_using_post_method_fixture: Response
) -> None:
    """
    Тестирование создания второго блюда в рамках теста проверки количества блюд и подменю в меню.

    Args:
        ac: клиент для асинхронных HTTP запросов,
        create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,
        create_second_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание блюда,

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
    target_submenu_id = get_created_object_attribute(response=create_submenu_using_post_method_fixture, attribute="id")

    await create_object_internal_test(
        create_object_using_post_method_fixture=create_second_dish_using_post_method_fixture,
        expected_data={
            "title": SECOND_DISH_TITLE_VALUE_TO_CREATE,
            "description": SECOND_DISH_DESCRIPTION_VALUE_TO_CREATE,
            "price": str(SECOND_DISH_PRICE_TO_CREATE),
            "submenu_id": target_submenu_id,
        },
    )


@pytest.mark.asyncio
async def test_get_specific_menu_from_check_quan_of_dishes_and_submenus_method(
        ac: AsyncClient,
        create_menu_using_post_method_fixture: Response,
        create_submenu_using_post_method_fixture: Response,
        create_dish_using_post_method_fixture: Response,
        create_second_dish_using_post_method_fixture: Response,
) -> None:
    """
    Функция тестирует получение определенного меню в рамках теста проверки количества блюд и подменю в меню.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. title найденной записи, которую вернул сервер, совпадает title'ом созданной ранее записи.
        3. description найденной записи, которую вернул сервер, совпадает description'ом созданной ранее записи.
        4. В ответе были данные о подменю, количестве подменю, а также количестве блюд, связанных с меню через все
           подменю.

    Args:
        ac: клиент для асинхронных HTTP запросов,
        create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,
        create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,
        create_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание блюда,
        create_second_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание 2-ого блюда,

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
    target_menu_id = get_created_object_attribute(response=create_menu_using_post_method_fixture, attribute="id")

    # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
    target_submenu_id = get_created_object_attribute(response=create_submenu_using_post_method_fixture, attribute="id")

    # Получаем uuid, который вернул сервер после создания записи в таблице dishes с помощью фикстуры.
    target_dish_id = get_created_object_attribute(response=create_dish_using_post_method_fixture, attribute="id")

    # Получаем uuid, который вернул сервер после создания записи в таблице dishes с помощью фикстуры.
    target_second_dish_id = get_created_object_attribute(
        response=create_second_dish_using_post_method_fixture,
        attribute="id"
    )

    url = f"/api/v1/menus/{target_menu_id}"

    response = await ac.get(url=url)

    assert_response(
        response=response,
        expected_status_code=200,
        expected_data={
            "id": target_menu_id,
            "title": MENU_TITLE_VALUE_TO_CREATE,
            "description": MENU_DESCRIPTION_VALUE_TO_CREATE,
            "submenus": [
                {
                    "id": target_submenu_id,
                    "title": SUBMENU_TITLE_VALUE_TO_CREATE,
                    "description": SUBMENU_DESCRIPTION_VALUE_TO_CREATE,
                    "menu_id": target_menu_id,
                    "dishes": [
                        {
                            "id": target_dish_id,
                            "title": DISH_TITLE_VALUE_TO_CREATE,
                            "description": DISH_DESCRIPTION_VALUE_TO_CREATE,
                            "price": str(DISH_PRICE_TO_CREATE),
                            "submenu_id": target_submenu_id
                        },
                        {
                            "id": target_second_dish_id,
                            "title": SECOND_DISH_TITLE_VALUE_TO_CREATE,
                            "description": SECOND_DISH_DESCRIPTION_VALUE_TO_CREATE,
                            "price": str(SECOND_DISH_PRICE_TO_CREATE),
                            "submenu_id": target_submenu_id
                        }
                    ]
                }
            ],
            "submenus_count": 1,
            "dishes_count": 2,
        },
    )


@pytest.mark.asyncio
async def test_get_specific_submenu_from_check_quan_of_dishes_and_submenus_method(
        ac: AsyncClient,
        create_menu_using_post_method_fixture: Response,
        create_submenu_using_post_method_fixture: Response,
        create_dish_using_post_method_fixture: Response,
        create_second_dish_using_post_method_fixture: Response,
) -> None:
    """
    Функция тестирует получение определенного подменю в рамках теста проверки количества блюд и подменю в меню.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. title найденной записи, которую вернул сервер, совпадает title'ом созданной ранее записи.
        3. description найденной записи, которую вернул сервер, совпадает description'ом созданной ранее записи.
        4. menu_id найденной записи, которую вернул сервер, совпадает menu_id созданной ранее записи.
        5. В ответе были данные о блюдах и их количестве

    Args:
        ac: клиент для асинхронных HTTP запросов,
        create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,
        create_submenu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание подменю,
        create_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание блюда,
        create_second_dish_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание 2-ого блюда,

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
    target_menu_id = get_created_object_attribute(response=create_menu_using_post_method_fixture, attribute="id")

    # Получаем uuid, который вернул сервер после создания записи в таблице submenus с помощью фикстуры.
    target_submenu_id = get_created_object_attribute(response=create_submenu_using_post_method_fixture, attribute="id")

    # Получаем uuid, который вернул сервер после создания записи в таблице dishes с помощью фикстуры.
    target_dish_id = get_created_object_attribute(response=create_dish_using_post_method_fixture, attribute="id")

    # Получаем uuid, который вернул сервер после создания записи в таблице dishes с помощью фикстуры.
    target_second_dish_id = get_created_object_attribute(
        response=create_second_dish_using_post_method_fixture,
        attribute="id"
    )

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
            "dishes": [
                {
                    "id": target_dish_id,
                    "title": DISH_TITLE_VALUE_TO_CREATE,
                    "description": DISH_DESCRIPTION_VALUE_TO_CREATE,
                    "price": str(DISH_PRICE_TO_CREATE),
                    "submenu_id": target_submenu_id
                },

                {
                    "id": target_second_dish_id,
                    "title": SECOND_DISH_TITLE_VALUE_TO_CREATE,
                    "description": SECOND_DISH_DESCRIPTION_VALUE_TO_CREATE,
                    "price": str(SECOND_DISH_PRICE_TO_CREATE),
                    "submenu_id": target_submenu_id
                }
            ],
            "dishes_count": 2,
        },
    )


@pytest.mark.asyncio
async def test_delete_submenu_from_check_quan_of_dishes_and_submenus_method(
        ac: AsyncClient,
        create_menu_using_post_method_fixture: Response,
        create_submenu_using_post_method_fixture: Response,
) -> None:
    """
    Тест удаления подменю в рамках теста проверки количества блюд и подменю в меню.

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
async def test_get_submenus_method_after_delete_from_check_quan_of_dishes_and_submenus_method(
        ac: AsyncClient,
        create_menu_using_post_method_fixture: Response
) -> None:
    """
    Тестирование события получения всех записей из таблицы submenus, когда запись была удалена из таблицы.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. Ответ содержит пустой список

    Args:
        ac: клиент для асинхронных HTTP запросов,
        create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
    target_menu_id = get_created_object_attribute(response=create_menu_using_post_method_fixture, attribute="id")

    url = f"/api/v1/menus/{target_menu_id}/submenus"
    await get_object_when_table_is_empty_internal_test(ac=ac, url=url)


@pytest.mark.asyncio
async def test_get_dishes_method_after_delete_submenu_from_check_quan_of_dishes_and_submenus_method(
        ac: AsyncClient,
        create_menu_using_post_method_fixture: Response,
        create_submenu_using_post_method_fixture: Response,
) -> None:
    """
    Тестирование события получения всех записей из таблицы dishes после удаления подменю, к которому блюда были
    привязаны.

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
async def test_get_specific_menu_after_delete_submenu_with_dishes_from_check_quan_of_dishes_and_submenus_method(
        ac: AsyncClient,
        create_menu_using_post_method_fixture: Response
) -> None:
    """
    Функция тестирует получение определенного меню после удаления подменю с блюдми.

    Тест проходит успешно, если:
        1. Код ответа 200.
        2. title найденной записи, которую вернул сервер, совпадает title'ом созданной ранее записи.
        3. description найденной записи, которую вернул сервер, совпадает description'ом созданной ранее записи.
        4. К меню не привязано подменю и блюда.

    Args:
        ac: клиент для асинхронных HTTP запросов.
        create_menu_using_post_method_fixture: фикстура с ответом сервера на POST запрос на создание меню,

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице menus c помощью фикстуры.
    target_menu_id = get_created_object_attribute(response=create_menu_using_post_method_fixture, attribute="id")

    url = f"/api/v1/menus/{target_menu_id}"

    response = await ac.get(url=url)

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
        },
    )


@pytest.mark.asyncio
async def test_delete_menu_from_check_quan_of_dishes_and_submenus_method(
        ac: AsyncClient,
        create_menu_using_post_method_fixture: Response
) -> None:
    """
    Тест удаления меню.

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

    url = f"/api/v1/menus/{target_menu_id}"

    # Используем тест, который тестирует удаление записи.
    await delete_object_internal_test(ac=ac, url=url)


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

    url = "/api/v1/menus"

    await get_object_when_table_is_empty_internal_test(ac=ac, url=url)
