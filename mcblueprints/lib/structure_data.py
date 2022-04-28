from dataclasses import dataclass, field
from typing import Optional

from mcblueprints.lib.block import Block
from mcblueprints.lib.nbt import NbtCompound
from mcblueprints.lib.vec import Vec3


@dataclass
class StructurePaletteEntry:
    index: int
    block: Block


@dataclass
class StructureBlockEntry:
    state: int
    pos: Vec3
    nbt: Optional[NbtCompound] = None


@dataclass
class StructureEntityEntry:
    pos: Vec3
    nbt: NbtCompound


@dataclass
class StructureData:
    size: Vec3
    palette: list[StructurePaletteEntry] = field(default_factory=list)
    blocks: list[StructureBlockEntry] = field(default_factory=list)
    entities: list[StructureEntityEntry] = field(default_factory=list)
