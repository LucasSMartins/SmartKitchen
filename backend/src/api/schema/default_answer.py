from typing import Dict, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from pydantic.dataclasses import dataclass
from src.api.schema.users import UserOut


class Default_Answer(BaseModel):
    status: str
    message: str
    data: list[UserOut]
