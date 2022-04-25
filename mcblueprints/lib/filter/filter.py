from abc import ABC, abstractmethod
from typing import List

from pyckaxe import BlockMap, ResolutionContext, Resource
from pydantic.main import BaseModel

__all__ = (
    "FilterRule",
    "Filter",
)


class FilterRule(BaseModel, ABC):
    @abstractmethod
    async def apply(self, ctx: ResolutionContext, block_map: BlockMap):
        """Apply the filter rule to `block_map`."""


class Filter(Resource):
    rules: List[FilterRule]

    async def apply(self, ctx: ResolutionContext, block_map: BlockMap):
        # Apply all rules, in order.
        for rule in self.rules:
            await rule.apply(ctx, block_map)
