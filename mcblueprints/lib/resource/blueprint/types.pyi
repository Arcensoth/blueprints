from typing import Dict, List, TypeAlias

from mcblueprints.lib.resource.blueprint.palette_entry.abc.blueprint_palette_entry import (
    BlueprintPaletteEntry,
)

BlueprintPalette: TypeAlias = Dict[str, BlueprintPaletteEntry]
BlueprintLayout: TypeAlias = List[List[str]]
