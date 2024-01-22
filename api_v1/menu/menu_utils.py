"""
Функции специфичные для модуля не относящиеся к бизнес-логике.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 22 января 2024
"""
from menu.models import Menu


def count_dishes(menu: Menu) -> int:
    """
    Функция для подсчета связанных с меню (не на прямую) блюд.

    Args:
        menu: объект, полученный в результате выборки

    Returns: кол-во блюд, связанных с подменю, которые связаны с меню.

    """
    dishes = 0

    for submenu in menu.submenus:
        dishes += submenu.dishes_counter

    return dishes
