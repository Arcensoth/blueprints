from abc import ABC, abstractmethod
from dataclasses import dataclass

from pyckaxe import BlockMap, ResolutionContext

__all__ = ("FilterRule",)


@dataclass(frozen=True)
class FilterRule(ABC):
    @abstractmethod
    async def apply(self, ctx: ResolutionContext, block_map: BlockMap):
        """Apply the filter rule to `block_map`."""
