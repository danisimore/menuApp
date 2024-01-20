import os
import sys

import uuid

from sqlalchemy import String, Column, UUID
from database.database import Base

sys.path.append(os.path.join(sys.path[0], "api_v1"))


class Menu(Base):
    __tablename__ = "menu"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
