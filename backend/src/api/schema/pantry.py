from enum import Enum

from pydantic import BaseModel


class Units(Enum):
    UNITS = "un"
    LITERS = "L"
    KILO_GRAMA = "kg"


class Items(BaseModel):
    item_name: str
    quantity: int
    unit: Units


class Subcategories(BaseModel):
    id: str
    category_name: str
    items: list[Items | None]


class Categories(BaseModel):
    categories: list[Subcategories]


class Pantry(BaseModel):
    user_id: str
    username: str
    pantry: Categories
