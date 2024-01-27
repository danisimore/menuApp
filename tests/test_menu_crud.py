"""
Модуль для тестирования CRUD операций, связанных с меню.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 27 января 2024
"""

import pytest
from httpx import AsyncClient, Response

TITLE_VALUE_TO_CREATE = "Test Menu #1"
DESCRIPTION_VALUE_TO_CREATE = "Description for the Test Menu #1"

TITLE_VALUE_TO_UPDATE = "Updated title for the Test Menu 1"
DESCRIPTION_VALUE_TO_UPDATE = "Updated description for the Test Menu 1"


def assert_menus_response(response: Response, expected_status_code: int, expected_data: list) -> None:
    """
    Функция для проверки на совпадение данных, возвращаемых серверов и данных, которые мы ожидаем увидеть в ответе.

    Args:
        response: ответ сервера,
        expected_status_code: ожидаемый статус код от сервера,
        expected_data: ожидаемые данные от сервера

    Returns:
        None
    """

    error_messages = {
        "wrong_response_body": f"Expected that response body would be equal to {expected_data}, "
                               f"but it is equal to {response.json()}",
        "wrong_status_code": f"It was expected that the status code would be {expected_status_code}, "
                             f"but it was received {response.status_code}",
    }

    assert response.status_code == expected_status_code, error_messages["wrong_status_code"]
    assert response.json() == expected_data, error_messages["wrong_response_body"]


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
            "title": TITLE_VALUE_TO_CREATE,
            "description": DESCRIPTION_VALUE_TO_CREATE,
        },
    )

    # Возвращаем ответ с данными.
    return response


@pytest.mark.asyncio
async def test_get_menus_method_when_table_is_empty(ac: AsyncClient) -> None:
    """
    Тестирование события получения всех записей из таблицы menus, когда в таблице еще нет ни одной записи.

    Тест проходит успешно, если:
        1. Код ответа 200;
        2. В теле ответа - пустой список.
    В случае неудачи выводится error_msg.

    Args:
        ac: клиент для асинхронных HTTP запросов.

    Returns:
        None
    """

    response = await ac.get(url="/api/v1/menus")

    assert_menus_response(response=response, expected_status_code=200, expected_data=[])


@pytest.mark.asyncio
async def test_create_menu_using_post_method(
        ac: AsyncClient, create_menu_using_post_method_fixture
) -> None:
    """
    Тестирование создания меню, путем отправки POST запроса.

    Тест проходит успешно, если:
        1. Код ответа 201;
        2. title созданной записи, которую вернул сервер, совпадает с переданным title'ом в запросе.
        3. description созданной записи, которую вернул сервер, совпадает с переданным description'ом в запросе.
    В случае неудачи выводится error_msg.

    Args:
        ac: клиент для асинхронных HTTP запросов.
        create_menu_using_post_method_fixture: фикстура, для отправки POST запроса и сохранения ответа сервера в кеше

    Returns:
        None
    """

    # Делаем POST запрос, используя фикстуру.
    response: Response = create_menu_using_post_method_fixture

    # Получаем uuid, который вернул сервер после создания записи в таблице menus.
    created_menu_id = response.json()["id"]

    assert_menus_response(
        response=response,
        expected_status_code=201,
        expected_data={
            "id": created_menu_id,
            "title": TITLE_VALUE_TO_CREATE,
            "description": DESCRIPTION_VALUE_TO_CREATE,
        }
    )


@pytest.mark.asyncio
async def test_get_menus_method_when_table_is_not_empty(ac: AsyncClient) -> None:
    """
    Тестирование события получения всех записей из таблицы menus, когда в таблице есть записи.

    Args:
        ac: клиент для асинхронных HTTP запросов.

    Returns:
        None
    """
    response = await ac.get(url="/api/v1/menus")

    assert response.status_code == 200 and len(response.json()) != 0


@pytest.mark.asyncio
async def test_get_specific_menu_method(
        ac: AsyncClient, create_menu_using_post_method_fixture
):
    """
    Тестирование получения определенной записи из таблицы menus по переданному параметру пути в запросе.

    Args:
        ac: клиент для асинхронных HTTP запросов.
        create_menu_using_post_method_fixture: фикстура, которая нужна для получения из кеша данных о созданной записи
        во время отправки POST запроса.

    Returns:

    """
    # Получаем меню, созданное во время тестирования POST запроса.
    created_menu_using_post_method: Response = create_menu_using_post_method_fixture
    # Получаем uuid этого меню.
    created_menu_id = created_menu_using_post_method.json()["id"]

    # Сохраняем ответ сервера, делая запрос с параметром uuid.
    response = await ac.get(url=f"/api/v1/menus/{created_menu_id}")

    assert_menus_response(
        response=response,
        expected_status_code=200,
        expected_data={
            "id": created_menu_id,
            "title": TITLE_VALUE_TO_CREATE,
            "description": DESCRIPTION_VALUE_TO_CREATE,
            "submenus": [],
            "submenus_count": 0,
            "dishes_count": 0,
        }
    )


@pytest.mark.asyncio
async def test_update_menu_using_patch_method(
        ac: AsyncClient, create_menu_using_post_method_fixture
) -> None:
    """
    Тестирование обновления записи с помощью отправки запроса с методом PATCH

    Args:
        ac: клиент для асинхронных HTTP запросов.

        create_menu_using_post_method_fixture: фикстура, которая нужна для получения из кеша данных о созданной записи
        во время отправки POST запроса.

    Returns:
        None
    """

    # Получаем меню, созданное во время тестирования POST запроса.
    created_menu_using_post_method: Response = create_menu_using_post_method_fixture

    # Получаем id
    created_menu_id = created_menu_using_post_method.json()["id"]

    response = await ac.patch(
        url=f"/api/v1/menus/{created_menu_id}",
        json={
            "title": TITLE_VALUE_TO_UPDATE,
            "description": DESCRIPTION_VALUE_TO_UPDATE,
        },
    )

    assert_menus_response(
        response=response,
        expected_status_code=200,
        expected_data={
            "id": created_menu_id,
            "title": TITLE_VALUE_TO_UPDATE,
            "description": DESCRIPTION_VALUE_TO_UPDATE,
        }
    )


@pytest.mark.asyncio
async def test_get_specific_menu_method_after_update(
        ac: AsyncClient, create_menu_using_post_method_fixture
) -> None:
    """
    Тестирование получения определенной записи из таблицы menus по переданному параметру пути в запросе.

    Args:
        ac: клиент для асинхронных HTTP запросов,

        create_menu_using_post_method_fixture: фикстура, которая нужна для получения из кеша данных о созданной записи
        во время отправки POST запроса.

    Returns:
        None
    """

    # Получаем меню, созданное вначале тестов.
    created_menu_using_post_method: Response = create_menu_using_post_method_fixture

    # Получаем его id.
    created_menu_id = created_menu_using_post_method.json()["id"]

    # Сохраняем ответ сервера, делая запрос с параметром uuid.
    response = await ac.get(url=f"/api/v1/menus/{created_menu_id}")

    assert_menus_response(
        response=response,
        expected_status_code=200,
        expected_data={
            "id": created_menu_id,
            "title": TITLE_VALUE_TO_UPDATE,
            "description": DESCRIPTION_VALUE_TO_UPDATE,
            "submenus": [],
            "submenus_count": 0,
            "dishes_count": 0,
        }
    )


@pytest.mark.asyncio
async def test_delete_menu_method(ac: AsyncClient, create_menu_using_post_method_fixture) -> None:
    """
    Тест удаления записи.

    Args:
        ac: клиент для асинхронных HTTP запросов.

        create_menu_using_post_method_fixture: фикстура, которая нужна для получения из кеша данных о созданной записи
        во время отправки POST запроса.

    Returns:
        None
    """

    # Получаем меню, созданное вначале.
    updated_menu_using_patch_method: Response = create_menu_using_post_method_fixture

    # Получаем uuid этого меню.
    updated_menu_uuid = updated_menu_using_patch_method.json()["id"]

    # Делаем запрос с методом DELETE.
    response = await ac.delete(url=f"/api/v1/menus/{updated_menu_uuid}")

    assert_menus_response(
        response=response,
        expected_status_code=200,
        expected_data={"status": "success!"}
    )


@pytest.mark.asyncio
async def test_get_menus_method_after_delete(ac: AsyncClient) -> None:
    """
    Тестирование события получения всех записей из таблицы menus, когда запись была удалена из таблицы.

    Args:
        ac: клиент для асинхронных HTTP запросов.

    Returns:
        None
    """

    response = await ac.get(url="/api/v1/menus")

    assert_menus_response(response=response, expected_status_code=200, expected_data=[])


@pytest.mark.asyncio
async def test_get_specific_menu_method_after_delete(
        ac: AsyncClient, create_menu_using_post_method_fixture
) -> None:
    """

    Args:
        ac: клиент для асинхронных HTTP запросов.

        create_menu_using_post_method_fixture: фикстура, которая нужна для получения из кеша данных о созданной записи
        во время отправки POST запроса.

    Returns:
        None
    """
    # Получаем данные меню из кеша, которое создавалось в начале тестов.
    created_menu_using_patch_method: Response = create_menu_using_post_method_fixture

    # Получаем uuid этого меню.
    created_menu_uuid = created_menu_using_patch_method.json()["id"]

    # Сохраняем ответ сервера, делая запрос с параметром uuid.
    response = await ac.get(url=f"/api/v1/menus/{created_menu_uuid}")

    assert_menus_response(
        response=response,
        expected_status_code=404,
        expected_data={"detail": "menu not found"}
    )
