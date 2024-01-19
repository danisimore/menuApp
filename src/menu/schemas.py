from pydantic import BaseModel


class MenuCreate(BaseModel):
    title: str
