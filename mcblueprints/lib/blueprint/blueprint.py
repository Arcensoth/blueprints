from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional, TypeAlias

from pyckaxe import BlockMap, Position, ResolutionContext, Resource, Structure
from pyckaxe.utils import ModuleClassifier
from pyckaxe.utils.validators.normalizer import Normalizer
from pydantic import BaseModel

__all__ = (
    "BlueprintPaletteEntry",
    "BlueprintPalette",
    "BlueprintLayout",
    "Blueprint",
)


class BlueprintPaletteEntry(BaseModel, ABC):
    key: str

    @classmethod
    def __get_validators__(cls):
        yield Normalizer(cls.normalize)
        yield ModuleClassifier(
            cls,
            type_field="type",
            default_module="mcblueprints.lib.blueprint.palette_entries",
            function_name="create",
        )

    @classmethod
    def normalize(cls, value: Any) -> Any:
        # A string is assumed to be a basic block.
        if isinstance(value, str):
            return dict(type="block", block=value)

    @abstractmethod
    async def merge(
        self, ctx: ResolutionContext, block_map: BlockMap, position: Position
    ):
        """Merge into `block_map` at `position`."""


BlueprintPalette: TypeAlias = dict[str, BlueprintPaletteEntry]
BlueprintLayout: TypeAlias = list[list[str]]


class Blueprint(Resource):
    size: Position
    palette: BlueprintPalette
    layout: BlueprintLayout
    anchor: Optional[Position] = None

    # TODO ensure palette keys are 1 char
    # TODO read the layout upside-down

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
