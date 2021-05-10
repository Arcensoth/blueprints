from dataclasses import dataclass
from typing import Any, AsyncIterable, Generic, Optional, Tuple, TypeVar

from pyckaxe.lib import (
    BlockMap,
    Namespace,
    Resource,
    ResourceLocation,
    Structure,
    StructureLocation,
)
from pyckaxe.lib.position import Position

from blueprints.lib.resource.blueprint.blueprint import Blueprint
from blueprints.lib.resource.blueprint.palette_entry.abc.blueprint_palette_entry import (
    BlueprintPalette,
    BlueprintPaletteEntry,
)
from blueprints.lib.resource.blueprint.palette_entry.blueprint_blueprint_palette_entry import (
    BlueprintBlueprintPaletteEntry,
)
from blueprints.lib.resource.blueprint.palette_entry.material_blueprint_palette_entry import (
    MaterialBlueprintPaletteEntry,
)
from blueprints.lib.resource.blueprint.palette_entry.void_blueprint_palette_entry import (
    VoidBlueprintPaletteEntry,
)
from blueprints.lib.resource.blueprint.types import BlueprintProcessingContext

__all__ = ("BlueprintTransformer",)


ResourceType = TypeVar("ResourceType", bound=Resource)
PaletteEntryType = TypeVar("PaletteEntryType", bound=BlueprintPaletteEntry)


@dataclass
class _MergeArgs(Generic[PaletteEntryType]):
    palette_entry: PaletteEntryType
    block_map: BlockMap
    position: Position
    palette_key: str
    palette: BlueprintPalette


# @implements ResourceTransformer[Blueprint]
@dataclass
class BlueprintTransformer:
    """
    Transforms a blueprint into a structure.

    Attributes
    ----------
    structure_serializer
        The structure serializer to use, including data version.
    generated_namespace
        A separate namespace to use for generated resources.
    generated_prefix_parts
        A prefix to apply to the locations of generated resources.
    """

    generated_namespace: Optional[str] = None
    generated_prefix_parts: Optional[Tuple[str, ...]] = None

    # @implements ResourceTransformer
    def __call__(
        self, ctx: BlueprintProcessingContext
    ) -> AsyncIterable[Tuple[Resource, ResourceLocation]]:
        return self.transform(ctx)

    async def transform(
        self, ctx: BlueprintProcessingContext
    ) -> AsyncIterable[Tuple[Resource, ResourceLocation]]:
        """ Turn the blueprint into a structure NBT file. """
        structure = await self.build_structure(ctx)
        structure_location = self.to_structure_location(ctx.location)
        yield structure, structure_location

    async def build_structure(self, ctx: BlueprintProcessingContext) -> Structure:
        # Flatten the blueprint into a block map, and turn that into a structure.
        block_map = await self.flatten_blueprint(ctx, ctx.resource)
        structure = Structure.from_block_map(block_map)
        return structure

    async def flatten_blueprint(
        self, ctx: BlueprintProcessingContext, blueprint: Blueprint
    ) -> BlockMap:
        # Create a new block map to hold the final state.
        block_map = BlockMap(size=blueprint.size)
        # Traverse palette entries in the order they are defined in the symbol table.
        for symbol, palette_key in blueprint.symbols.items():
            palette_entry = blueprint.palette[palette_key]
            # Scan over the blueprint once per entry, looking for matching symbols.
            for offset in blueprint.scan(symbol):
                # Merge the palette entry into the block map at the offset.
                await self.merge_palette_entry(
                    ctx,
                    _MergeArgs[Any](
                        palette_entry=palette_entry,
                        block_map=block_map,
                        position=offset,
                        palette_key=palette_key,
                        palette=blueprint.palette,
                    ),
                )
        return block_map

    async def merge_palette_entry(
        self, ctx: BlueprintProcessingContext, args: _MergeArgs[Any]
    ):
        if isinstance(args.palette_entry, VoidBlueprintPaletteEntry):
            await self.merge_void_palette_entry(ctx, args)
        elif isinstance(args.palette_entry, MaterialBlueprintPaletteEntry):
            await self.merge_material_palette_entry(ctx, args)
        elif isinstance(args.palette_entry, BlueprintBlueprintPaletteEntry):
            await self.merge_blueprint_palette_entry(ctx, args)

    async def merge_void_palette_entry(
        self,
        ctx: BlueprintProcessingContext,
        args: _MergeArgs[VoidBlueprintPaletteEntry],
    ):
        # Void the block in the block map.
        args.block_map.void(args.position)

    async def merge_material_palette_entry(
        self,
        ctx: BlueprintProcessingContext,
        args: _MergeArgs[MaterialBlueprintPaletteEntry],
    ):
        # Resolve the material.
        material = await ctx[args.palette_entry.material]
        # Set the corresponding block in the block map.
        args.block_map.set_block(args.position, material.block, args.palette_key)

    async def merge_blueprint_palette_entry(
        self,
        ctx: BlueprintProcessingContext,
        args: _MergeArgs[BlueprintBlueprintPaletteEntry],
    ):
        # Resolve the child blueprint.
        child_blueprint = await ctx[args.palette_entry.blueprint]

        # Flatten the child blueprint into its own block map independently.
        child_block_map = await self.flatten_blueprint(ctx, child_blueprint)

        # If filter keys are present, remove everything else.
        filter_keys = args.palette_entry.filter_keys
        if filter_keys:
            child_block_map.filter(filter_keys)

        # Use the replace keys to replace entries, in the order they are defined.
        replace_keys = args.palette_entry.replace_keys
        if replace_keys:
            for child_palette_key, parent_palette_key in replace_keys.items():
                parent_palette_entry = args.palette[parent_palette_key]
                # Scan over the block map, looking for matching keys.
                for offset in child_block_map.scan(child_palette_key):
                    # Merge the parent palette entry back into the child block map at
                    # the same position.
                    await self.merge_palette_entry(
                        ctx,
                        _MergeArgs[Any](
                            palette_entry=parent_palette_entry,
                            block_map=child_block_map,
                            position=offset,
                            palette_key=parent_palette_key,
                            palette=child_blueprint.palette,
                        ),
                    )

        # Merge the converted child block map into the parent block map.
        args.block_map.merge(child_block_map, args.position - args.palette_entry.offset)

    def to_structure_location(self, location: ResourceLocation) -> StructureLocation:
        # Map the blueprint location to a structure location.
        namespace = Namespace(name=self.generated_namespace or location.namespace.name)
        parts = location.parts
        if self.generated_prefix_parts:
            parts = (*self.generated_prefix_parts, *parts)
        structure_location = ResourceLocation(namespace, parts)
        return Structure @ structure_location
