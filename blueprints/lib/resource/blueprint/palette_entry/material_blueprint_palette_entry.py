from dataclasses import dataclass

from blueprints.lib.resource.blueprint.palette_entry.abc.blueprint_palette_entry import (
    BlueprintPaletteEntry,
)
from blueprints.lib.resource.material.types import MaterialOrLocation

__all__ = ("MaterialBlueprintPaletteEntry",)


@dataclass
class MaterialBlueprintPaletteEntry(BlueprintPaletteEntry):
    material: MaterialOrLocation
