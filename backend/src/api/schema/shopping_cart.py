from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl
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


class Units(str, Enum):
    UNITS = "un"
    LITERS = "L"
    MILLILITER = "ml"
    GRAMS = "g"
    KILO_GRAMS = "kg"


class ItemsIn(BaseModel):
    item_name: str = Field(
        ..., min_length=2, max_length=15, pattern=r"^([a-zA-Z0-9À-ÖØ-öø-ÿ ])+$"
    )
    quantity: int
    unit: Units
    price: Decimal
    # icon: HttpUrl


class ItemsOut(ItemsIn):
    item_id: PydanticObjectId
    price: str


class Categories(BaseModel):
    category_name: str
    items: list[ItemsOut] = []


class ShoppingCart(BaseModel):
    user_id: PydanticObjectId
    username: str
    pantry: list[Categories]


"""
    TODO:  Faz sentido ser um link o icon ou um SVG armazenado no banco ?
"""
