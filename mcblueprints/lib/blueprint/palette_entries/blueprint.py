from typing import Any, Optional

from pyckaxe import BlockMap, Position, ResolutionContext, ResourceLink

from mcblueprints import Blueprint, BlueprintPaletteEntry, Filter


class BlueprintBlueprintPaletteEntry(BlueprintPaletteEntry):
    blueprint: ResourceLink[Blueprint]
    offset: Optional[Position] = None
    filter: Optional[ResourceLink[Filter]] = None

    # @implements BlueprintPaletteEntry
    async def merge(
        self, ctx: ResolutionContext, block_map: BlockMap, position: Position
    ):
        # Resolve the child blueprint.
        child_blueprint = await self.blueprint(ctx)

        # Flatten the child blueprint into its own block map independently.
        child_block_map = await child_blueprint.flatten(ctx)

        # If a filter is present, apply it to the child block map before merging it.
        if self.filter is not None:
            filter = await self.filter(ctx)
            await filter.apply(ctx, child_block_map)

        # Account for the child's anchor and our own offset.
        child_offset = position
        if child_blueprint.anchor is not None:
            child_offset -= child_blueprint.anchor
        if self.offset is not None:
            child_offset -= self.offset

        # Merge the converted child block map into the parent block map.
        block_map.merge(child_block_map, child_offset)


def create(data: Any) -> BlueprintPaletteEntry:
    return BlueprintBlueprintPaletteEntry.parse_obj(data)
