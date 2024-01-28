import os

from decimal import Decimal
from typing import Union

from httpx import Response, AsyncClient


def assert_response(response: Response, expected_status_code: int, expected_data: list) -> None:
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


def get_created_object_attribute(response: Response, attribute: str) -> Union[str, int, Decimal]:
    """
    Функция возвращает указанный атрибут объекта из тела ответа.

    Args:
        response: ответ сервера (фикстура, представляющая собой закешированый ответ сервера на запрос)
        attribute: атрибут объекта, который необходимо получить

    Returns:
        Атрибут созданного объекта, который был запрошен в качестве переданного аргумента.
    """
    create_object_response: Response = response

    created_object_attribute = create_object_response.json()[attribute]

    return created_object_attribute


def save_created_menu_id(create_menu_using_post_method_fixture: Response) -> str:
    """
    Функция сохраняет id созданного меню в переменной окружения и возвращает его в виде строки.

    Args:
        create_menu_using_post_method_fixture: фикстура, для отправки POST запроса на создание меню.

    Returns:
        str -> uuid созданного меню
    """

    target_menu_id = get_created_object_attribute(
        response=create_menu_using_post_method_fixture,
        attribute="id"
    )
    os.environ["TARGET_MENU_ID"] = target_menu_id

    return target_menu_id


async def test_get_menus_when_table_is_empty(ac: AsyncClient) -> None:
    """
    Функция для проверки запроса на получение всех меню, когда таблица пуста.

    Args:
        ac: клиент для асинхронных HTTP запросов.

    Returns:
        None
    """
    response = await ac.get(url="/api/v1/menus")
    assert_response(response=response, expected_status_code=200, expected_data=[])
