from dataclasses import dataclass
from typing import List

from pyckaxe import BlockMap, ResolutionContext

from mcblueprints.lib.resource.filter.rule.abc.filter_rule import FilterRule
from mcblueprints.lib.resource.material.material import MaterialLink

__all__ = ("KeepMaterialsFilterRule",)


@dataclass(frozen=True)
class KeepMaterialsFilterRule(FilterRule):
    materials: List[MaterialLink]

    async def apply(self, ctx: ResolutionContext, block_map: BlockMap):
        materials = [await material(ctx) for material in self.materials]
        blocks = [material.block for material in materials]
        block_map.keep_blocks(blocks)
