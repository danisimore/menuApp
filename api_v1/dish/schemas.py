from pydantic import BaseModel
from decimal import Decimal


class CreateDish(BaseModel):
    title: str
    description: str
    price: Decimal


class UpdateDish(BaseModel):
    title: str
    description: str
    price: Decimal
