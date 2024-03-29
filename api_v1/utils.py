"""
Модуль для описания функций не связанных с бизнес-логикой. Нормализация данных, приведение их к нужному типу и т.д.
Общий для всех приложений.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 06 февраля 2024
"""
from typing import Any

from dish.models import Dish
from dish.schemas import CreateDish
from menu.models import Menu
from submenu.models import Submenu
from submenu.schemas import CreateSubmenu
from submenu.submenu_utils import format_dishes


def get_created_object_dict(created_object: Menu | Dish | Submenu) -> dict[Any, Any]:
    """
    Функция формирует словарь из таблицы для созданной записи.

    Args:
        created_object: Объект, который был создан, путем отправки пользователем POST запроса.

    Returns: Словарь, который содержит пары название_колонки:значение_колонки для созданного объекта.

    """

    created_object_columns = created_object.__table__.columns

    created_object_dict = {
        column.key: str(getattr(created_object, column.key))
        if getattr(created_object, column.key) is not None
        else None
        for column in created_object_columns
    }

    return created_object_dict


def create_dict_from_received_data(
        received_data: CreateSubmenu | CreateDish, parent_id: str, foreign_key_field_name: str
) -> dict[Any, Any]:
    """
    Функция формирует словарь на основе полученных от клиента данных о блюде, которое нужно создать

    Args:
        received_data: полученные данные от клиента для создания блюда,
        parent_id: uuid объекта, для которого создается текущий.
        foreign_key_field_name: название поля со ссылкой на объект, для которого создается текущий

    Returns:
        Словарь с данными о новом блюде
    """

    data_dict = received_data.model_dump()

    data_dict[foreign_key_field_name] = parent_id

    return data_dict


async def format_object_to_json(objects_list: list[Any] | dict[Any, Any]) -> list[dict[Any, Any]]:
    """
    Метод для приведение объектов в списке к типу dict.

    Args:
        objects_list: список с объектом

    Returns:
        Список объектов типа dict.
    """

    object_json_list = []
    for obj in objects_list:
        if hasattr(obj, 'dishes'):
            formatted_dishes = await format_dishes(obj.dishes)
            obj_json = await obj.json()
            obj_json['dishes'] = formatted_dishes

            object_json_list.append(obj_json)
        else:
            object_json_list.append(await obj.json())

    return object_json_list
