from enum import Enum
from typing import Dict

from pydantic import BaseModel


class StatusMsg(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    FAIL = "fail"


class DefaultAnswer(BaseModel):
    status: StatusMsg
    msg: str
    data: list[Dict] | None = None
