from pydantic import BaseModel


class MenuCreate(BaseModel):
    title: str
    description: str


class MenuUpdate(BaseModel):
    title: str
    description: str
