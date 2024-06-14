from enum import Enum
from typing import Annotated, Optional
from uuid import UUID, uuid4

from bson import ObjectId
from bson.objectid import ObjectId as BsonObjectId
from pydantic import BaseModel, BeforeValidator, Field, field_validator
from pydantic_mongo import AbstractRepository, PydanticObjectId


class Units(str, Enum):
    UNITS = "un"
    LITERS = "L"
    MILLILITER = "ml"
    GRAMS = "g"
    KILO_GRAMS = "kg"


class ItemsOut(BaseModel):
    # PydanticObjectId is an alias to Annotated[ObjectId, ObjectIdAnnotation]
    item_id: PydanticObjectId
    item_name: str
    quantity: int
    unit: Units


class ItemsIn(BaseModel):
    item_name: str
    quantity: int
    unit: Units


class Categories(BaseModel):
    category_name: str
    items: list[ItemsOut] = []


class Pantry(BaseModel):
    user_id: PydanticObjectId
    username: str
    pantry: list[Categories]
