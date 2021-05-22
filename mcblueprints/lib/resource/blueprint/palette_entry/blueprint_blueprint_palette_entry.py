from dataclasses import dataclass
from typing import Optional

from pyckaxe import BlockMap, Position, ResolutionContext

from mcblueprints.lib.resource.blueprint.palette_entry.abc.blueprint_palette_entry import (
    BlueprintPaletteEntry,
)
from mcblueprints.lib.resource.blueprint.types import BlueprintOrLocation
from mcblueprints.lib.resource.filter.types import FilterOrLocation

__all__ = ("BlueprintBlueprintPaletteEntry",)


@dataclass
class BlueprintBlueprintPaletteEntry(BlueprintPaletteEntry):
    blueprint: BlueprintOrLocation
    offset: Position
    filter: Optional[FilterOrLocation] = None

    async def merge(
        self, ctx: ResolutionContext, block_map: BlockMap, position: Position
    ):
        # Resolve the child blueprint.
        child_blueprint = await ctx[self.blueprint]

        # Flatten the child blueprint into its own block map independently.
        child_block_map = await child_blueprint.flatten(ctx)

        # If a filter is present, apply it to the child block map before merging it.
        if self.filter is not None:
            filter = await ctx[self.filter]
            await filter.apply(ctx, child_block_map)

        # Merge the converted child block map into the parent block map.
        child_offset = position - self.offset - child_blueprint.anchor
        block_map.merge(child_block_map, child_offset)
