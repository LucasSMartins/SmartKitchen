from typing import Dict, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from pydantic.dataclasses import dataclass
from src.api.schema.users import UserOut


class Attr_Default_Answer(BaseModel):
    status: str
    msg: str
    data: list[UserOut | Dict] | None = None
    loc: list[str | int] | None = None
    type: str | None = None


class Default_Answer(BaseModel):
    detail: Attr_Default_Answer
