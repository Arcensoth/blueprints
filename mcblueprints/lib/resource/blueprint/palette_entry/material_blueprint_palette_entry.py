from dataclasses import dataclass

from pyckaxe import BlockMap, Position, ResolutionContext

from mcblueprints.lib.resource.blueprint.palette_entry.abc.blueprint_palette_entry import (
    BlueprintPaletteEntry,
)
from mcblueprints.lib.resource.material.material import MaterialLink

__all__ = ("MaterialBlueprintPaletteEntry",)


@dataclass
class MaterialBlueprintPaletteEntry(BlueprintPaletteEntry):
    material: MaterialLink

    async def merge(
        self, ctx: ResolutionContext, block_map: BlockMap, position: Position
    ):
        # Resolve the material.
        material = await self.material(ctx)
        # Set the corresponding block in the block map.
        block_map[position] = material.block
