from typing import Any

from pydantic import BaseModel


class Attr_Default_Answer(BaseModel):
    status: str
    msg: str
    data: list[Any] | None = None
    loc: list[str | int] | None = None
    type: str | None = None


class Default_Answer(BaseModel):
    detail: Attr_Default_Answer
    # model_config = ConfigDict(arbitrary_types_allowed=True)
