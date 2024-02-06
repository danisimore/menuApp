"""
Функции специфичные для модуля не относящиеся к бизнес-логике.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 29 января 2024 - добавлена функция для преобразования цен блюд из Decimal к строке
"""


def convert_prices_to_str(submenu) -> None:
    """
    Функция преобразует цены блюд из Decimal к строке, для того чтобы не терять десятичные нули, т.к. необходимо
    выводить 2 знака после запятой

    Args:
        submenu: объект записи из таблицы submenus

    Returns:
        None
    """
    for dish in submenu.dishes:
        dish.price = str(dish.price)


async def format_dishes(dishes: list) -> list[dict]:
    """
    Функция для преобразования блюд к словарю (json).

    Returns:
        список с объектами блюд в формате словаря
    """
    dishes_list = []
    for dish in dishes:
        dishes_list.append(await dish.json())

    return dishes_list
