"""
Модуль дополнительного функционала тестирования.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 29 января 2024
"""

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
