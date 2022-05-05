from typing import Any, Iterable, Optional

from pydantic import validator

from mcblueprints.lib.block_state import BlockState, BlockStateValue
from mcblueprints.lib.nbt import NbtCompound, to_nbt
from mcblueprints.lib.normalizable_model import NormalizableModel
from mcblueprints.lib.utils import is_submapping

__all__ = ["Block"]


class Block(NormalizableModel):
    name: str
    state: Optional[BlockState] = None
    data: Optional[NbtCompound] = None

    @classmethod
    def normalize_input(cls, value: Any) -> Any:
        if isinstance(value, str):
            return dict(name=value)
        return value

    @validator("data", pre=True)
    def data_to_nbt(cls, value: Any):
        if value is not None:
            return to_nbt(value)
        return value

    def __str__(self) -> str:
        return "".join(self._str_parts())

    def _str_parts(self) -> Iterable[str]:
        yield self.name
        if self.state is not None:
            yield str(self.state)
        if self.data is not None:
            yield str(self.data.snbt())  # type: ignore

    def matches(self, other: "Block") -> bool:
        """Check whether this `Block` is a subset of another."""
        if self.name != other.name:
            return False
        if other.state is not None:
            if self.state is not None:
                return self.state.matches(other.state)
            return False
        if other.data is not None:
            if self.data is not None:
                return is_submapping(self.data, other.data)
            return False
        return True

    def matches_any_of(self, others: list["Block"]) -> bool:
        """Check whether this `Block` is a subset of any others."""
        return any(self.matches(other) for other in others)

    def matches_all_of(self, others: list["Block"]) -> bool:
        """Check whether this `Block` is a subset of all others."""
        return all(self.matches(other) for other in others)

    def with_state(self, **states: BlockStateValue) -> "Block":
        """Return a new block with its own state."""
        return self.copy(update=dict(state=BlockState(__root__=states)))
