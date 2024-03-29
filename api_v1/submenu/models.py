"""
Модуль для описания класса модели БД.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 20 января 2024
"""

import uuid
from typing import Any

from menu.models import Base
from sqlalchemy import UUID, Column, ForeignKey, String
from sqlalchemy.orm import relationship


class Submenu(Base):
    __tablename__ = 'submenus'

    id = Column(
        UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4
    )
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

    menu_id = Column(
        UUID(as_uuid=True),
        ForeignKey('menus.id', ondelete='CASCADE'),
        nullable=False,
        primary_key=False,
    )

    menu = relationship(argument='Menu', back_populates='submenus')

    dishes = relationship(
        argument='Dish', cascade='all,delete', back_populates='submenu', lazy='selectin'
    )

    async def json(self) -> dict[Any, Any]:
        """
        Функция преобразует объект Submenu в словарь.

        Returns:
            Словарь с данными об объекте
        """

        if hasattr(self, 'dishes_count'):
            return {
                'id': str(self.id),
                'title': self.title,
                'description': self.description,
                'dishes': self.dishes,
                'dishes_count': self.dishes_count,
                'menu_id': str(self.menu_id),
            }
        else:
            return {
                'id': str(self.id),
                'title': self.title,
                'description': self.description,
                'dishes': self.dishes,
                'menu_id': str(self.menu_id),
            }
