from re import search as re_search

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserIn(BaseModel):
    username: str = Field(..., min_length=5, max_length=15)
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("password")
    def validate_password(cls, value):
        if not re_search(r"[A-Z]", value):
            raise ValueError(
                "The password should contain at least one uppercase letter"
            )
        if not re_search(r"[a-z]", value):
            raise ValueError(
                "The password should contain at least one lowercase letter"
            )
        if not re_search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError("The password must contain at least one special character")
        if not re_search(r"[0-9]", value):
            raise ValueError("The password must contain at least one number")

        return value


class UserOut(BaseModel):
    username: str
    email: EmailStr


class UserInUpdate(UserIn):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
