"""
Модуль для тестов, которые повторяются в тестировании меню, подменю и блюд. Необходим для избежания дублирования кода.
Тесты не отрабатывают из этого модуля, а эвэйтятся в основных тестовых модулях, поэтому назвал их внутренними.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 30 января 2024 | Избавился от общих переменных.
"""

from httpx import AsyncClient, Response

from .test_data import MENU_TITLE_VALUE_TO_CREATE, MENU_DESCRIPTION_VALUE_TO_CREATE

from .utils import get_created_object_attribute


def assert_response(
    response: Response, expected_status_code: int, expected_data: list
) -> None:
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

    assert response.status_code == expected_status_code, error_messages[
        "wrong_status_code"
    ]
    assert response.json() == expected_data, error_messages["wrong_response_body"]


async def get_object_when_table_is_empty_internal_test(
    ac: AsyncClient, url: str
) -> None:
    """
    Тестирование получения объектов из пустой таблицы.

    Args:
        ac: клиент для асинхронных HTTP запросов,
        url: url, по которому нужно получить объекты.
    Returns:
        None
    """
    response = await ac.get(url=url)
    assert_response(response=response, expected_status_code=200, expected_data=[])

    return response


async def create_object_internal_test(
    create_object_using_post_method_fixture: Response,
    expected_data: dict,
) -> None:
    """
    Функция для создания записи в таблице БД.

    Args:
        create_object_using_post_method_fixture: закешированый ответ сервера на POST запрос.

        expected_data: ожидаемый результат в ответе от сервера

    Returns:
        None
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице и сохраняем его в переменной окружения.
    target_object_id = get_created_object_attribute(
        response=create_object_using_post_method_fixture, attribute="id"
    )

    # К ожидаемым данным добавляем этот uuid
    expected_data["id"] = target_object_id

    # Проверяем, что данные в ответе на POST запрос соответствуют ожидаемым
    assert_response(
        response=create_object_using_post_method_fixture,
        expected_status_code=201,
        expected_data=expected_data,
    )


async def delete_object_internal_test(ac: AsyncClient, url: str) -> None:
    """
    Тестирование удаления объекта.

    Args:
        ac: клиент для асинхронных HTTP запросов,
        url: эндпоинт для удаления объекта.

    Returns:
        None
    """

    response: Response = await ac.delete(url)

    assert_response(
        response=response,
        expected_status_code=200,
        expected_data={"status": "success!"},
    )


async def get_objects_when_table_is_not_empty_internal_test(
    ac: AsyncClient, url: str
) -> None:
    """
    Тестирование получения объектов из таблицы, в которой есть записи.

    Args:
        ac: клиент для асинхронных HTTP запросов,
        url: эндпоинт, из которого нужно получить данные

    Returns:
        None
    """

    response: Response = await ac.get(url=url)

    assert response.status_code == 200 and len(response.json()) > 0

    return response


async def get_specific_object_when_table_is_empty_internal_test(
    ac: AsyncClient, url: str, expected_data: dict
) -> None:
    """
    Тестирование получения определенного объекта из пустой таблицы.

    Args:
        ac: клиент для асинхронных HTTP запросов,
        url: эндпоинт из которого нужно получить данные,
        expected_data: ожидаемый результат в ответе от сервера

    Returns:
        None
    """
    response = await ac.get(url=url)

    assert_response(
        response=response, expected_status_code=404, expected_data=expected_data
    )
