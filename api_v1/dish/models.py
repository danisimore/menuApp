import uuid

from sqlalchemy import Column, UUID, String, ForeignKey

from submenu.models import Base


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4(), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

    submenu_id = Column(UUID(as_uuid=True), ForeignKey("submenu.id"), nullable=False)
