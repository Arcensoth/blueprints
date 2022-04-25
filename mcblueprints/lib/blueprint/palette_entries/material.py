from typing import Any

from pyckaxe import BlockMap, Position, ResolutionContext, ResourceLink

from mcblueprints import BlueprintPaletteEntry, Material


class MaterialBlueprintPaletteEntry(BlueprintPaletteEntry):
    material: ResourceLink[Material]

    # @implements BlueprintPaletteEntry
    async def merge(
        self, ctx: ResolutionContext, block_map: BlockMap, position: Position
    ):
        # Resolve the material.
        material = await self.material(ctx)

        # Set the corresponding block in the block map.
        block_map[position] = material.block


def create(data: Any) -> BlueprintPaletteEntry:
    return MaterialBlueprintPaletteEntry.parse_obj(data)
