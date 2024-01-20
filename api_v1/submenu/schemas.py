from pydantic import BaseModel


class CreateSubmenu(BaseModel):
    title: str
    description: str


class UpdateSubmenu(BaseModel):
    title: str
    description: str
