from dataclasses import dataclass
from typing import List, TypeAlias

from pyckaxe import BlockMap, ResolutionContext, Resource, ResourceLink

from mcblueprints.lib.resource.filter.rule.abc.filter_rule import FilterRule

__all__ = (
    "Filter",
    "FilterLink",
)


@dataclass
class Filter(Resource):
    rules: List[FilterRule]

    async def apply(self, ctx: ResolutionContext, block_map: BlockMap):
        # Apply all rules, in order.
        for rule in self.rules:
            await rule.apply(ctx, block_map)


FilterLink: TypeAlias = ResourceLink[Filter]
