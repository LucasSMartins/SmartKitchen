from enum import Enum
from typing import Any

from bson import ObjectId
from pydantic import BaseModel


class Units(str, Enum):
    UNITS = "un"
    LITERS = "L"
    MILLILITER = "ml"
    GRAMS = "g"
    KILO_GRAMS = "kg"


class Items(BaseModel):
    item_name: str
    quantity: int
    unit: Units


class Categories(BaseModel):
    category_name: str
    items: list[Items] = []


class Pantry(BaseModel):
    user_id: str
    username: str
    pantry: list[Categories]
