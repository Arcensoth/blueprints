from typing import Any

from pydantic import BaseModel

__all__ = ["Blueprint"]


class Blueprint(BaseModel):
    size: tuple[int, int, int]
    palette: Any
    layout: Any
