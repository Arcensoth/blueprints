from dataclasses import dataclass
from typing import List

from pyckaxe import Block, BlockMap, ResolutionContext

from mcblueprints.lib.resource.filter.rule.abc.filter_rule import FilterRule

__all__ = ("KeepBlocksFilterRule",)


@dataclass(frozen=True)
class KeepBlocksFilterRule(FilterRule):
    blocks: List[Block]

    async def apply(self, ctx: ResolutionContext, block_map: BlockMap):
        block_map.keep_blocks(self.blocks)
