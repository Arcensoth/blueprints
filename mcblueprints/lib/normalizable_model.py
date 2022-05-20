from typing import Any

from pydantic import BaseModel
from pydantic.generics import GenericModel

__all__ = [
    "NormalizableModel",
    "NormalizableGenericModel",
]


class NormalizableModel(BaseModel):
    """A model that normalizes input before validation."""

    @classmethod
    def normalize_input(cls, value: Any) -> Any:
        return value

    # @overrides BaseModel
    @classmethod
    def _enforce_dict_if_root(cls, obj: Any) -> Any:
        return super()._enforce_dict_if_root(cls.normalize_input(obj))


class NormalizableGenericModel(GenericModel):
    """A generic model that normalizes input before validation."""

    @classmethod
    def normalize_input(cls, value: Any) -> Any:
        return value

    # @overrides BaseModel
    @classmethod
    def _enforce_dict_if_root(cls, obj: Any) -> Any:
        return super()._enforce_dict_if_root(cls.normalize_input(obj))
