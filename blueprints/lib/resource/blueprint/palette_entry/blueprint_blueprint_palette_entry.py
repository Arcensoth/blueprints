from dataclasses import dataclass
from typing import Dict, Set

from pyckaxe.lib import Position

from blueprints.lib.resource.blueprint.palette_entry.abc.blueprint_palette_entry import (
    BlueprintPaletteEntry,
)
from blueprints.lib.resource.blueprint.types import BlueprintOrLocation

__all__ = ("BlueprintBlueprintPaletteEntry",)


@dataclass
class BlueprintBlueprintPaletteEntry(BlueprintPaletteEntry):
    blueprint: BlueprintOrLocation
    offset: Position
    filter_keys: Set[str]
    replace_keys: Dict[str, str]
