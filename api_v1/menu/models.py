"""
Модуль для описания класса модели БД.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 20 января 2024
"""

import os
import sys

import uuid

from sqlalchemy import String, Column, UUID
from sqlalchemy.ext.hybrid import hybrid_property
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

    @hybrid_property
    def submenu_count(self) -> int:
        """
        Функция для подсчета кол-ва привязанных подменю к меню.

        Returns: int

        """
        return len(self.submenus)
