"""
Функции специфичные для модуля не относящиеся к бизнес-логике.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 29 января 2024 - добавлена функция для преобразования цен блюд из Decimal к строке
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


def convert_prices_to_str(menu) -> None:
    """
    Функция преобразует цены блюд из Decimal к строке, для того чтобы не терять десятичные нули, т.к. необходимо
    выводить 2 знака после запятой

    Args:
        menu: объект записи из таблицы menus

    Returns:
        None
    """
    for submenu in menu.submenus:
        for dish in submenu.dishes:
            dish.price = str(dish.price)
