from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, Field
from typing_extensions import Annotated

from mcblueprints.lib.material import Material
from mcblueprints.lib.normalizable_model import NormalizableModel

__all__ = ["Filter"]


class Filter(NormalizableModel):
    __root__: Annotated[
        Union[
            "Reference",
            "Group",
            "Keep",
            "Remove",
            "Replace",
        ],
        Field(discriminator="type"),
    ]

    @classmethod
    def normalize_input(cls, value: Any) -> Any:
        if isinstance(value, str):
            return dict(type="reference", name=value)
        if isinstance(value, list):
            return dict(type="group", children=value)  # type: ignore
        return value


class FilterBase(BaseModel):
    description: Optional[str]


class Reference(FilterBase):
    """Reference another filter."""

    type: Literal["reference"]

    name: str


class Group(FilterBase):
    """Group multiple filters together."""

    type: Literal["group"]

    children: list[Filter]


class Keep(FilterBase):
    """Keep blocks of a certain type."""

    type: Literal["keep"]

    keep: list[Material]


class Remove(FilterBase):
    """Remove blocks of a certain type."""

    type: Literal["remove"]

    remove: list[Material]


class Replace(FilterBase):
    """Replace blocks of a certain type with another type."""

    type: Literal["replace"]

    replace: list[Material]
    replacement: Material


Filter.update_forward_refs()
