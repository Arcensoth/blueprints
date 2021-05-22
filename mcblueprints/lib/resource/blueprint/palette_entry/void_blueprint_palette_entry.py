from dataclasses import dataclass

from pyckaxe import BlockMap, Position, ResolutionContext

from mcblueprints.lib.resource.blueprint.palette_entry.abc.blueprint_palette_entry import (
    BlueprintPaletteEntry,
)

__all__ = ("VoidBlueprintPaletteEntry",)


@dataclass
class VoidBlueprintPaletteEntry(BlueprintPaletteEntry):
    async def merge(
        self, ctx: ResolutionContext, block_map: BlockMap, position: Position
    ):
        # Void the block in the block map.
        del block_map[position]
