"""
Модуль для описания класса модели БД.

Автор: danisimore || Danil Vorobyev || danisimore@yandex.ru
Дата: 20 января 2024
"""

import uuid

from sqlalchemy import String, UUID, ForeignKey, Column
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from menu.models import Base


class Submenu(Base):
    __tablename__ = "submenus"

    id = Column(
        UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4
    )
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

    menu_id = Column(
        UUID(as_uuid=True),
        ForeignKey("menus.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=False,
    )

    menu = relationship(argument="Menu", back_populates="submenus")

    dishes = relationship(
        argument="Dish", cascade="all,delete", back_populates="submenu"
    )

    @hybrid_property
    def dishes_counter(self) -> int:
        """
        Функция для подсчета блюд, привязанных к подменю

        Returns: int

        """
        return len(self.dishes)
