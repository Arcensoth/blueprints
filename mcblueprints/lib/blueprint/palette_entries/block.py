from typing import Any

from pyckaxe import Block, BlockMap, Position, ResolutionContext

from mcblueprints import BlueprintPaletteEntry


class BlockBlueprintPaletteEntry(BlueprintPaletteEntry):
    block: Block

    # @implements BlueprintPaletteEntry
    async def merge(
        self, ctx: ResolutionContext, block_map: BlockMap, position: Position
    ):
        # Set the corresponding block in the block map.
        block_map[position] = self.block


def create(data: Any) -> BlueprintPaletteEntry:
    return BlockBlueprintPaletteEntry.parse_obj(data)
