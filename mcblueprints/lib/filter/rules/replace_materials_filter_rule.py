from dataclasses import dataclass
from typing import List

from pyckaxe import BlockMap, ResolutionContext

from mcblueprints.lib.resource.filter.rule.abc.filter_rule import FilterRule
from mcblueprints.lib.resource.material.material import MaterialLink

__all__ = ("ReplaceMaterialsFilterRule",)


@dataclass(frozen=True)
class ReplaceMaterialsFilterRule(FilterRule):
    materials: List[MaterialLink]
    replacement: MaterialLink

    async def apply(self, ctx: ResolutionContext, block_map: BlockMap):
        materials = [await block(ctx) for block in self.materials]
        blocks = [material.block for material in materials]
        replacement_material = await self.replacement(ctx)
        replacement_block = replacement_material.block
        block_map.replace_blocks(blocks, replacement_block)
