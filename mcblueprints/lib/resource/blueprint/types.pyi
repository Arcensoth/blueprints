from typing import Dict, List

from mcblueprints.lib.resource.blueprint.palette_entry.abc.blueprint_palette_entry import (
    BlueprintPaletteEntry,
)

BlueprintPalette = Dict[str, BlueprintPaletteEntry]
BlueprintLayout = List[List[str]]
