"""
Модуль для описания функций не связанных с бизнес-логикой. Нормализация данных, приведение их к нужному типу и т.д.
Общий для всех приложений.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 20 января 2024
"""
from typing import Union

from dish.models import Dish
from menu.models import Menu
from submenu.models import Submenu


def get_created_object_dict(created_object: Union[Menu, Dish, Submenu]) -> dict:
    """
    Функция формирует словарь из таблицы для созданной записи.

    Args:
        created_object: Объект, который был создан, путем отправки пользователем POST запроса.

    Returns: Словарь, который содержит пары название_колонки:значение_колонки для созданного объекта.

    """

    # Переменная, которая хранит все столбцы таблицы созданной записи
    created_object_columns = created_object.__table__.columns

    # Итерируемся по названиям столбцов таблицы;
    # Если колонка только что созданного объекта не None, то создаем пару название_столбца:занчение_столбца
    # Иначе явно устанавливаем значение None, чтобы в БД хранилось значение null
    created_object_dict = {
        column.key: str(getattr(created_object, column.key))
        if getattr(created_object, column.key) is not None
        else None
        for column in created_object_columns
    }

    return created_object_dict
