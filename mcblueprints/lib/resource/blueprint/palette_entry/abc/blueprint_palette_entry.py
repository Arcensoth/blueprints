from abc import ABC, abstractmethod
from dataclasses import dataclass

from pyckaxe import BlockMap, Position, ResolutionContext

__all__ = ("BlueprintPaletteEntry",)


@dataclass
class BlueprintPaletteEntry(ABC):
    key: str

    @abstractmethod
    async def merge(
        self, ctx: ResolutionContext, block_map: BlockMap, position: Position
    ):
        """Merge into `block_map` at `position`."""
