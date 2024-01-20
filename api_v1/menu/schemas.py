"""
Модуль для описания pydantic классов.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 20 января 2024
"""

from pydantic import BaseModel


class MenuCreate(BaseModel):
    title: str
    description: str


class MenuUpdate(BaseModel):
    title: str
    description: str
