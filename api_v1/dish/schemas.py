"""
Модуль для описания Pydantic классов, для валидации данных блюд.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 22 января 2024
"""

from decimal import Decimal

from pydantic import BaseModel


class CreateDish(BaseModel):
    title: str
    description: str
    price: Decimal


class UpdateDish(BaseModel):
    title: str
    description: str
    price: Decimal
