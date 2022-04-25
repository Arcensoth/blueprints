from dataclasses import dataclass
from typing import AsyncIterable, Optional, Tuple, TypeVar

from pyckaxe import Resource, ResourceLocation, ResourceProcessingContext

from mcblueprints.lib.blueprint.blueprint import Blueprint, BlueprintPaletteEntry

__all__ = ("BlueprintTransformer",)


ResourceT = TypeVar("ResourceT", bound=Resource)
PaletteEntryT = TypeVar("PaletteEntryT", bound=BlueprintPaletteEntry)


# @implements ResourceTransformer[Blueprint]
@dataclass
class BlueprintTransformer:
    """
    Transforms a blueprint into a structure.

    Attributes
    ----------
    generated_namespace
        A separate namespace to use for generated resources.
    generated_prefix_parts
        A prefix to apply to the locations of generated resources.
    """

    generated_namespace: Optional[str] = None
    generated_prefix_parts: Optional[Tuple[str, ...]] = None

    # @implements ResourceTransformer
    def __call__(
        self, ctx: ResourceProcessingContext[Blueprint]
    ) -> AsyncIterable[Tuple[Resource, ResourceLocation]]:
        return self.transform(ctx)

    async def transform(
        self, ctx: ResourceProcessingContext[Blueprint]
    ) -> AsyncIterable[Tuple[Resource, ResourceLocation]]:
        """Turn the blueprint into a structure NBT file."""
        structure = await ctx.resource.to_structure(ctx)
        structure_location = self.to_structure_location(ctx.location)
        yield structure, structure_location

    def to_structure_location(self, location: ResourceLocation) -> ResourceLocation:
        # Map the blueprint location to a structure location.
        namespace = self.generated_namespace or location.namespace
        parts = location.parts
        if self.generated_prefix_parts:
            parts = (*self.generated_prefix_parts, *parts)
        structure_location = ResourceLocation(namespace=namespace, parts=parts)
        return structure_location
