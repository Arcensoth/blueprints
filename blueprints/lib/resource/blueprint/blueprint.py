from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from pyckaxe.lib import Position, Resource

from blueprints.lib.resource.blueprint.palette_entry.abc.blueprint_palette_entry import (
    BlueprintPalette,
)
from blueprints.lib.resource.material.types import MaterialOrLocation

__all__ = (
    "BlueprintSymbolMap",
    "BlueprintLayout",
    "Blueprint",
)


BlueprintSymbolMap = Dict[str, str]
BlueprintLayout = List[List[str]]


@dataclass
class Blueprint(Resource):
    size: Position
    palette: BlueprintPalette
    symbols: BlueprintSymbolMap
    layout: BlueprintLayout

    structure_pivot: Optional[Position]
    residue_mask: Optional[MaterialOrLocation]

    def scan(self, symbol: str) -> Iterable[Position]:
        for y, floor in enumerate(self.layout):
            for x, row in enumerate(floor):
                yield from (
                    Position.from_xyz(x, y, z) for z, s in enumerate(row) if s == symbol
                )
