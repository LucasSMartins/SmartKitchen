from enum import Enum

from pydantic import BaseModel, Field, field_validator
from pydantic_mongo import PydanticObjectId


class CategoryValue(int, Enum):
    CANDY = 101
    FROZEN = 102
    DRINKS = 103
    LAUNDRY = 104
    MEAT_FISH = 105
    DAIRY_EGGS = 106
    GROCERY_PRODUCTS = 107
    PERSONAL_HYGIENE = 108
    GRAINS_CEREALS = 109
    CLEANING_MATERIALS = 110
    FRUITS_VEGETABLES = 111
    CONDIMENTS_SAUCES = 112
    PASTA_WHEAT_PRODUCTS = 113
    BREADS_BAKERY_PRODUCTS = 114
    CANNED_GOODS_PRESERVES = 115


# TODO Deixo como opcional entre um e outro ou faço uma conversão?
class Units(str, Enum):
    UNITS = "un"
    LITERS = "l"
    MILLILITER = "ml"
    GRAMS = "g"
    KILO_GRAMS = "kg"


class ItemsOut(BaseModel):
    item_id: PydanticObjectId
    item_name: str
    quantity: int
    unit: Units


class ItemsIn(BaseModel):
    item_name: str = Field(
        ..., min_length=2, max_length=15, pattern=r"^([a-zA-Z0-9À-ÖØ-öø-ÿ ])+$"
    )
    quantity: int
    unit: Units


# class ItemsInUpdate(ItemsIn):
#     item_name: str | None = None
#     quantity: int | None = None
#     unit: Units | None = None


class Categories(BaseModel):
    category_name: str
    items: list[ItemsOut] = []


class Pantry(BaseModel):
    user_id: PydanticObjectId
    username: str
    pantry: list[Categories]
