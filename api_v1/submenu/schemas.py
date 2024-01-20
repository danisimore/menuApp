from pydantic import BaseModel


class CreateSubmenu(BaseModel):
    title: str
    description: str
