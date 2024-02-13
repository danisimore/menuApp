"""
Модуль для описания pydantic классов.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 20 января 2024
"""

from pydantic import UUID4, BaseModel


class MenusGet(BaseModel):
    id: UUID4
    title: str
    description: str


class MenuSpecificGet(MenusGet):
    submenus_count: int
    dishes_count: int


class MenuCreate(BaseModel):
    title: str
    description: str


class MenuUpdate(BaseModel):
    title: str
    description: str
