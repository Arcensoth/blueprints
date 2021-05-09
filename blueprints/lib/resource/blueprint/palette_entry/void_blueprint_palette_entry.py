from dataclasses import dataclass

from blueprints.lib.resource.blueprint.palette_entry.abc.blueprint_palette_entry import (
    BlueprintPaletteEntry,
)

__all__ = ("VoidBlueprintPaletteEntry",)


@dataclass
class VoidBlueprintPaletteEntry(BlueprintPaletteEntry):
    pass
