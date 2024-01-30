"""
Модуль для описания класса модели БД.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 20 января 2024
"""

import os
import sys

import uuid

from sqlalchemy import String, Column, UUID
from sqlalchemy.orm import relationship

from database.database import Base

sys.path.append(os.path.join(sys.path[0], "api_v1"))


class Menu(Base):
    __tablename__ = "menus"

    id = Column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False
    )
    title = Column(String, nullable=False)
    description = Column(String)

    submenus = relationship(
        argument="Submenu", cascade="all,delete", back_populates="menu"
    )

    def json(self):

        if hasattr(self, 'submenus_count') and hasattr(self, 'dishes_count'):
            return {
                "id": str(self.id),
                "title": self.title,
                "description": self.description,
                "submenus_count": self.submenus_count,
                "dishes_count": self.dishes_count,
            }
        else:
            return {
                "id": str(self.id),
                "title": self.title,
                "description": self.description,
            }
