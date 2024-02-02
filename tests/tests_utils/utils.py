"""
Модуль дополнительного функционала тестирования.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 29 января 2024
"""

import os

from httpx import Response


def get_created_object_attribute(response: Response, attribute: str) -> str:
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


def save_created_object_id(
    create_object_using_post_method_fixture: Response, env_name: str
) -> str:
    """
    Функция сохраняет id созданного меню в переменной окружения и возвращает его в виде строки.

    Args:
        create_object_using_post_method_fixture: фикстура, для отправки POST запроса на создание меню.
        env_name: Название переменной окружения, которая будет содержать идентификатор объекта
    Returns:
        str -> uuid созданного меню
    """

    # Получаем uuid, который вернул сервер после создания записи в таблице.
    target_object_id = get_created_object_attribute(
        response=create_object_using_post_method_fixture, attribute='id'
    )

    # Сохраняем его в переменную окружения, чтобы использовать его в следующих тестах
    os.environ[env_name] = target_object_id

    return target_object_id
