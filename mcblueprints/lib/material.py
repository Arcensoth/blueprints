from typing import Any, Optional

from mcblueprints.lib.normalizable_model import NormalizableModel

__all__ = ["Material"]


class Material(NormalizableModel):
    name: str
    state: Optional[dict[str, Any]]
    nbt: Optional[dict[str, Any]]

    @classmethod
    def normalize_input(cls, value: Any) -> Any:
        if isinstance(value, str):
            return dict(name=value)
        return value
