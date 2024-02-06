"""
Функции специфичные для модуля не относящиеся к бизнес-логике.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 29 января 2024 - добавлена функция для преобразования цен блюд из Decimal к строке
"""

from dish.models import Dish


async def format_dishes(dishes: list[Dish]) -> list[dict]:
    """
    Функция для преобразования блюд к словарю (json).

    Returns:
        список с объектами блюд в формате словаря
    """

    dishes_list = []
    for dish in dishes:
        dishes_list.append(await dish.json())

    return dishes_list
