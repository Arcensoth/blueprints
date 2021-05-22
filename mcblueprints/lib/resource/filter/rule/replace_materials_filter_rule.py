from dataclasses import dataclass
from typing import List

from pyckaxe import BlockMap, ResolutionContext

from mcblueprints.lib.resource.filter.rule.abc.filter_rule import FilterRule
from mcblueprints.lib.resource.material.types import MaterialOrLocation

__all__ = ("ReplaceMaterialsFilterRule",)


@dataclass(frozen=True)
class ReplaceMaterialsFilterRule(FilterRule):
    materials: List[MaterialOrLocation]
    replacement: MaterialOrLocation

    async def apply(self, ctx: ResolutionContext, block_map: BlockMap):
        materials = [await ctx[block] for block in self.materials]
        blocks = [material.block for material in materials]
        replacement_material = await ctx[self.replacement]
        replacement_block = replacement_material.block
        block_map.replace_blocks(blocks, replacement_block)
