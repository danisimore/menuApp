"""
Модуль для описания модели таблицы БД, содержащей данные о блюдах.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 06 февраля 2024
"""

import uuid

from sqlalchemy import DECIMAL, UUID, Column, ForeignKey, String
from sqlalchemy.orm import relationship
from submenu.models import Base


class Dish(Base):
    __tablename__ = 'dishes'

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

    price = Column(DECIMAL(precision=15, scale=2), nullable=False)

    submenu_id = Column(
        UUID(as_uuid=True),
        ForeignKey(column='submenus.id', ondelete='CASCADE'),
        nullable=False,
        primary_key=False,
    )

    submenu = relationship(argument='Submenu', back_populates='dishes')

    async def json(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'price': str(self.price),
            'submenu_id': str(self.submenu_id),
        }
