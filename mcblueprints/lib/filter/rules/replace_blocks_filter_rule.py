from dataclasses import dataclass
from typing import List

from pyckaxe import Block, BlockMap, ResolutionContext

from mcblueprints.lib.resource.filter.rule.abc.filter_rule import FilterRule

__all__ = ("ReplaceBlocksFilterRule",)


@dataclass(frozen=True)
class ReplaceBlocksFilterRule(FilterRule):
    blocks: List[Block]
    replacement: Block

    async def apply(self, ctx: ResolutionContext, block_map: BlockMap):
        block_map.replace_blocks(self.blocks, self.replacement)
