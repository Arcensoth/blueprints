from dataclasses import dataclass
from typing import Dict, Iterable, List

from pyckaxe import BlockMap, Position, ResolutionContext, Resource, Structure

from mcblueprints.lib.resource.blueprint.palette_entry.abc.blueprint_palette_entry import (
    BlueprintPaletteEntry,
)

__all__ = (
    "BlueprintPalette",
    "BlueprintLayout",
    "Blueprint",
)


BlueprintPalette = Dict[str, BlueprintPaletteEntry]
BlueprintLayout = List[List[str]]


@dataclass
class Blueprint(Resource):
    size: Position
    anchor: Position
    palette: BlueprintPalette
    layout: BlueprintLayout

    def scan(self, symbol: str) -> Iterable[Position]:
        """Scan over the blueprint, looking for a particular symbol."""
        for y, floor in enumerate(self.layout):
            for x, row in enumerate(floor):
                yield from (
                    Position.from_xyz(x, y, z) for z, s in enumerate(row) if s == symbol
                )

    async def flatten(self, ctx: ResolutionContext) -> BlockMap:
        # Create a new block map to hold the final state.
        block_map = BlockMap(size=self.size)
        # Traverse palette entries in the order they are defined.
        for palette_key, palette_entry in self.palette.items():
            # Scan over the blueprint once per entry, looking for matching symbols.
            for offset in self.scan(palette_key):
                # Merge the palette entry into the block map at the offset.
                await palette_entry.merge(ctx, block_map, offset)
        return block_map

    async def to_structure(self, ctx: ResolutionContext) -> Structure:
        # Flatten the blueprint into a block map, and turn that into a structure.
        block_map = await self.flatten(ctx)
        structure = Structure.from_block_map(block_map)
        return structure
