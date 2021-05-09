from dataclasses import dataclass
from typing import Dict

__all__ = (
    "BlueprintPalette",
    "BlueprintPaletteEntry",
)


BlueprintPalette = Dict[str, "BlueprintPaletteEntry"]


@dataclass
class BlueprintPaletteEntry:
    key: str
