from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from pydantic.dataclasses import dataclass


class UserIn(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    username: str
    email: EmailStr


# @dataclass
# class User:
#     username: str
#     password: str
#     email: EmailStr
#     full_name: str | None = None
#     create_in: datetime = Field(default_factory=datetime.now)
