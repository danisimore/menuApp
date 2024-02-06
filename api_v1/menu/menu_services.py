"""
Бизнес логика, специфичная для модуля.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 06 февраля 2024
"""

from menu.models import Menu


async def parse_menu_data(menu_data: list[tuple[Menu, int, int]]) -> Menu | None:
    """
    Парсит полученный список с кортежем, в котором хранится Объект, счетчик подменю и блюд

    :param menu_data: список с кортежем, в котором хранится Объект, счетчик подменю и блюд
    :return: если в ходе выборки нашлось меню, то меню с добавленными атрибутами submenus_count и dishes_count
    """
    if menu_data:
        menu = menu_data[0][0]
        menu.submenus_count = menu_data[0][1]
        menu.dishes_count = menu_data[0][2]

        return menu

    return None
