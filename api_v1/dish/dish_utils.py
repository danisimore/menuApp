"""
Функции специфичные для модуля не относящиеся к бизнес-логике.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 11 февраля 2024 | Добавлена функция для применения скидки к цене блюда
"""
from decimal import Decimal
from typing import Any

from fastapi.responses import JSONResponse
from services import get_cache


async def apply_discount(dishes: list[dict[Any, Any]]) -> list[dict[Any, Any]]:
    """
    Применяет скидку к цене блюда, если для этого блюда скидка существует

    :param dishes: блюда, к ценам которых необходимо применить скидку
    :return: Список с данными о блюдах в JSON формате
    """

    for dish in dishes:
        discount_cache_key = 'discount_' + dish['id']

        discount_cache = await get_cache(key=discount_cache_key)

        if discount_cache:
            discount = float(dish['price']) / 100 * float(discount_cache)
            price_with_discount = float(dish['price']) - discount
            formatted_price_with_discount = str(f'{price_with_discount:.2f}')
            dish['price'] = formatted_price_with_discount

    return dishes


def format_decimal(value: type[Decimal]) -> str:
    """
    Функция, которая округляет цену до 2-х знаков после запятой.

    Args:
        value: цена.

    Returns: Строка.

    """
    return f'{value:.2f}'


def return_404_menu_not_linked_to_submenu() -> JSONResponse:
    """
    Функция, для возврата статус кода 404, если указанный идентификатор меню, не привязан у указанному идентификатору
    подменю.

    Returns: JSONResponse

    """

    return JSONResponse(
        content={
            'detail': 'the menu object with the identifier you passed has no connection with '
                      'the submenu object whose identifier you passed'
        },
        status_code=404,
    )
