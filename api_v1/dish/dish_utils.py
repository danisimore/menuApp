"""
Функции специфичные для модуля не относящиеся к бизнес-логике.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 22 января 2024
"""

from decimal import Decimal

from fastapi.responses import JSONResponse


def format_decimal(value: Decimal) -> str:
    """
    Функция, которая округляет цену до 2-х знаков после запятой.

    Args:
        value: цена.

    Returns: Строка.

    """
    return "{:.2f}".format(value)


def return_404_menu_not_linked_to_submenu() -> JSONResponse:
    """
    Функция, для возврата статус кода 404, если указанный идентификатор меню, не привязан у указанному идентификатору
    подменю.

    Returns:J SONResponse

    """

    return JSONResponse(
        content={
            "detail": "the menu object with the identifier you passed has no connection with "
            "the submenu object whose identifier you passed"
        },
        status_code=404,
    )
