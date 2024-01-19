import uuid
from sqlalchemy import String, Column, UUID
from database import Base


class Menu(Base):
    __tablename__ = "menu"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
