from decimal import Decimal


def format_decimal(value: Decimal) -> str:
    return "{:.2f}".format(value)

