"""
Модуль для описания pydantic классов.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 13 февраля 2024 | Добавлен docsting
"""


from pydantic import BaseModel


class CreateSubmenu(BaseModel):
    title: str
    description: str


class UpdateSubmenu(BaseModel):
    title: str
    description: str
