from typing import Any, MutableMapping

from pydantic import BaseModel, Field

from mcblueprints.lib.nbt import NbtCompound, NbtString
from mcblueprints.lib.utils import is_submapping

__all__ = ["BlockState"]


class BlockState(BaseModel, MutableMapping[str, Any]):
    __root__: dict[str, Any] = Field(default_factory=dict)

    def __str__(self) -> str:
        innards = ",".join(
            f"{k}={self._stringify_value(v)}" for k, v in self.__root__.items()
        )
        return f"[{innards}]"

    # @implements MutableMapping
    def __setitem__(self, key: str, value: Any):
        self.__root__.__setitem__(key, value)

    # @implements MutableMapping
    def __getitem__(self, key: str) -> Any:
        return self.__root__.__getitem__(key)

    # @implements MutableMapping
    def __delitem__(self, key: str):
        self.__root__.__delitem__(key)

    # @implements MutableMapping
    def __len__(self):
        return self.__root__.__len__()

    # @implements MutableMapping
    def __iter__(self):  # type: ignore
        return self.__root__.__iter__()

    def _stringify_value(self, value: Any) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    def matches(self, other: "BlockState") -> bool:
        """Check whether this `BlockState` is a subset of another."""
        return is_submapping(self, other)

    def to_nbt(self) -> NbtCompound:
        nbt_compound = NbtCompound()
        for key, value in self.items():
            # NOTE All block state property values are encoded as strings in NBT.
            stringified_value = self._stringify_value(value)
            nbt_compound[key] = NbtString(stringified_value)
        return nbt_compound
