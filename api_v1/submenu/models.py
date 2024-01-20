import uuid

from sqlalchemy import String, UUID, ForeignKey, Column
from menu.models import Base


class Submenu(Base):
    __tablename__ = "submenu"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4(), primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

    menu_id = Column(UUID(as_uuid=True), ForeignKey("menu.id"), nullable=False)
