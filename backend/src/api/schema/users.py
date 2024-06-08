import re
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, constr, field_validator
from datetime import datetime
from pydantic.dataclasses import dataclass


class UserIn(BaseModel):
    username: str = Field(
        ..., min_length=5, max_length=15, pattern=r"^([a-zA-Z0-9_ ])*$"
    )
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("password")
    def validate_password(cls, value):
        if not re.search(r"[A-Z]", value):
            raise ValueError(
                "The password should contain at least one uppercase letter"
            )
        if not re.search(r"[a-z]", value):
            raise ValueError(
                "The password should contain at least one lowercase letter"
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError("The password must contain at least one special character")
        if not re.search(r"[0-9]", value):
            raise ValueError("The password must contain at least one number")

        return value


class UserOut(BaseModel):
    username: str
    email: EmailStr
