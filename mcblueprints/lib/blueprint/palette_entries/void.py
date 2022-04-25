from typing import Any

from pyckaxe import BlockMap, Position, ResolutionContext

from mcblueprints import BlueprintPaletteEntry


class VoidBlueprintPaletteEntry(BlueprintPaletteEntry):
    # @implements BlueprintPaletteEntry
    async def merge(
        self, ctx: ResolutionContext, block_map: BlockMap, position: Position
    ):
        # Void the block in the block map.
        del block_map[position]


def create(data: Any) -> BlueprintPaletteEntry:
    return VoidBlueprintPaletteEntry.parse_obj(data)
