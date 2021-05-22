from dataclasses import dataclass

from pyckaxe import Block, BlockMap, Position, ResolutionContext

from mcblueprints.lib.resource.blueprint.palette_entry.abc.blueprint_palette_entry import (
    BlueprintPaletteEntry,
)

__all__ = ("BlockBlueprintPaletteEntry",)


@dataclass
class BlockBlueprintPaletteEntry(BlueprintPaletteEntry):
    block: Block

    async def merge(
        self, ctx: ResolutionContext, block_map: BlockMap, position: Position
    ):
        # Set the corresponding block in the block map.
        block_map[position] = self.block
