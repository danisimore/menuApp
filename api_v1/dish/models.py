import uuid

from sqlalchemy import Column, UUID, String, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, backref

from submenu.models import Base


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

    price = Column(DECIMAL(5, 2), nullable=False)

    submenu_id = Column(
        UUID(as_uuid=True), ForeignKey("submenu.id", ondelete="CASCADE"), nullable=False, primary_key=False
    )

    submenu = relationship("Submenu", back_populates="dishes")
