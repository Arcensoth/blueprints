from dataclasses import dataclass
from typing import AsyncIterable, Optional, Tuple, TypeVar

from pyckaxe import Namespace, Resource, ResourceLocation, Structure, StructureLocation

from mcblueprints.lib.resource.blueprint.palette_entry.abc.blueprint_palette_entry import (
    BlueprintPaletteEntry,
)
from mcblueprints.lib.resource.blueprint.types import BlueprintProcessingContext

__all__ = ("BlueprintTransformer",)


ResourceType = TypeVar("ResourceType", bound=Resource)
PaletteEntryType = TypeVar("PaletteEntryType", bound=BlueprintPaletteEntry)


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
        """Turn the blueprint into a structure NBT file."""
        structure = await ctx.resource.to_structure(ctx)
        structure_location = self.to_structure_location(ctx.location)
        yield structure, structure_location

    def to_structure_location(self, location: ResourceLocation) -> StructureLocation:
        # Map the blueprint location to a structure location.
        namespace = Namespace(name=self.generated_namespace or location.namespace.name)
        parts = location.parts
        if self.generated_prefix_parts:
            parts = (*self.generated_prefix_parts, *parts)
        structure_location = ResourceLocation(namespace, parts)
        return Structure @ structure_location
