import string
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, ClassVar, DefaultDict, Iterable, Iterator, Literal, Optional

from beet import Structure

from mcblueprints.lib.block import Block
from mcblueprints.lib.block_state import BlockState
from mcblueprints.lib.structure_data import (
    StructureBlockEntry,
    StructureData,
    StructurePaletteEntry,
)
from mcblueprints.lib.vec import Vec3
from mcblueprints.utils.nbt import NbtCompound

__all__ = ["BlockMap"]


@dataclass
class BlockMap:
    size: Vec3[int] | Literal["auto"]

    # y -> x -> z
    block_map: DefaultDict[int, DefaultDict[int, dict[int, Block]]]

    SYMBOLS: ClassVar[str] = string.digits + string.ascii_letters

    @classmethod
    def from_structure(cls, structure: Structure) -> "BlockMap":
        size_nbt: Any = structure.data["size"]
        size = Vec3[int](int(size_nbt[0]), int(size_nbt[1]), int(size_nbt[2]))
        block_map = BlockMap(size=size)

        palette_nbt: list[dict[str, Any]] = structure.data["palette"]
        blocks_nbt: list[dict[str, Any]] = structure.data["blocks"]
        cached_blocks: dict[int, Block] = {}
        for block_entry_nbt in blocks_nbt:
            pos_nbt: tuple[Any, ...] = block_entry_nbt["pos"]
            pos = Vec3[int](int(pos_nbt[0]), int(pos_nbt[1]), int(pos_nbt[2]))
            palette_idx = int(block_entry_nbt["state"])

            cached_block = cached_blocks.get(palette_idx)
            if not cached_block:
                palette_entry_nbt = palette_nbt[palette_idx]
                block_name = str(palette_entry_nbt["Name"])
                block_state: Optional[BlockState] = None
                properties_nbt: Optional[dict[str, Any]] = palette_entry_nbt.get(
                    "Properties"
                )
                if properties_nbt:
                    block_state = BlockState()
                    for key_nbt, value_nbt in properties_nbt.items():
                        block_state[str(key_nbt)] = str(value_nbt)
                cached_block = Block(name=block_name, state=block_state)
                cached_blocks[palette_idx] = cached_block

            block_data: Optional[NbtCompound] = block_entry_nbt.get("nbt")
            if block_data:
                block_map[pos] = cached_block.with_data(block_data)
            else:
                block_map[pos] = cached_block

        return block_map

    def __init__(self, size: Vec3[int] | Literal["auto"]):
        self.size = size
        self.block_map = defaultdict(lambda: defaultdict(dict))

    def __str__(self) -> str:
        return self.to_ascii()

    def __setitem__(self, key: Vec3[int], value: Block):
        if not self.in_bounds(key):
            raise ValueError(f"Position {key} exceeds block map size {self.size}")
        self.block_map[key.y][key.x][key.z] = value

    def __getitem__(self, key: Vec3[int]) -> Block:
        return self.block_map[key.y][key.x][key.z]

    def __delitem__(self, key: Vec3[int]):
        del self.block_map[key.y][key.x][key.z]

    def __iter__(self) -> Iterator[tuple[Vec3[int], Block]]:
        for y, layer in self.block_map.items():
            for x, row in layer.items():
                for z, block in row.items():
                    yield Vec3[int](x, y, z), block

    def in_bounds(self, position: Vec3[int]) -> bool:
        if self.size == "auto":
            return True
        size = self.size
        return (
            (0 <= position.x < size.x)
            and (0 <= position.y < size.y)
            and (0 <= position.z < size.z)
        )

    @property
    def is_empty(self) -> bool:
        return len(self.block_map) == 0

    @property
    def corners(self) -> tuple[Vec3[int], Vec3[int]]:
        if self.is_empty:
            raise ValueError("Cannot calculate corners of empty block map")

        positions = (pos for pos, _ in self)
        first_pos = next(positions)

        x_max, x_min = first_pos.x, first_pos.x
        y_max, y_min = first_pos.y, first_pos.y
        z_max, z_min = first_pos.z, first_pos.z

        for pos in positions:
            x_max, x_min = max(x_max, pos.x), min(x_min, pos.x)
            y_max, y_min = max(y_max, pos.y), min(y_min, pos.y)
            z_max, z_min = max(z_max, pos.z), min(z_min, pos.z)

        low = Vec3[int](x_min, y_min, z_min)
        high = Vec3[int](x_max, y_max, z_max)

        return low, high

    @property
    def actual_size(self) -> Vec3[int]:
        if self.size != "auto":
            return self.size
        if self.is_empty:
            return Vec3[int](0, 0, 0)
        low, high = self.corners
        return high - low + 1

    def get(self, key: Vec3[int]) -> Optional[Block]:
        row = self.block_map[key.y][key.x]
        return row.get(key.z)

    def remove_blocks(self, blocks: list[Block]):
        # Collect positions to remove first because we can't mutate during iteration.
        positions: list[Vec3[int]] = []
        for pos, block in self:
            if block.matches_any_of(blocks):
                del self[pos]
        for pos in positions:
            del self[pos]

    def keep_blocks(self, blocks: list[Block]):
        # Collect positions to remove first because we can't mutate during iteration.
        positions: list[Vec3[int]] = []
        for pos, block in self:
            if not block.matches_any_of(blocks):
                positions.append(pos)
        for pos in positions:
            del self[pos]

    def replace_blocks(self, blocks: list[Block], replacement: Block):
        # Collect positions to replace first because we can't mutate during iteration.
        positions: list[Vec3[int]] = []
        for pos, block in self:
            if block.matches_any_of(blocks):
                positions.append(pos)
        for pos in positions:
            self[pos] = replacement

    def scan(self, block: Block) -> Iterable[Vec3[int]]:
        yield from (pos for pos, b in self if b == block)

    def merge(self, other: "BlockMap", position: Optional[Vec3[int]] = None):
        position = position or Vec3[int](0, 0, 0)
        for offset, block in other:
            self[position + offset] = block

    def to_ascii(self) -> str:
        next_symbol_index = 0
        symbol_by_block: dict[Block, str] = {}
        layers: list[str] = []
        low, high = self.corners
        for y in range(low.y, high.y):
            rows: list[str] = []
            for x in range(low.x, high.x):
                line: str = ""
                for z in range(low.z, high.z):
                    block = self.get(Vec3[int](x, y, z))
                    if block is None:
                        line += "."
                        continue
                    symbol = symbol_by_block.get(block)
                    if symbol is None:
                        symbol = self.SYMBOLS[next_symbol_index]
                        next_symbol_index = (next_symbol_index + 1) % len(self.SYMBOLS)
                        symbol_by_block[block] = symbol
                    line += symbol
                rows.append(line)
            layer = "\n".join(rows)
            layers.append(layer)
        reversed_layers = reversed(layers)
        output = "\n\n".join(reversed_layers)
        return output

    def to_structure_data(self) -> StructureData:
        # Create the flat list of blocks, building a minimal palette as we go.
        palette_map: dict[str, StructurePaletteEntry] = {}
        blocks: list[StructureBlockEntry] = []
        low, _ = self.corners
        for pos, block in self:
            # Recalibrate auto-sized structures.
            actual_pos = pos
            if self.size == "auto":
                actual_pos -= low
            # Grab the corresponding palette entry from the palette map.
            palette_map_key = (
                block.name if block.state is None else f"{block.name}{block.state}"
            )
            palette_map_entry = palette_map.get(palette_map_key)
            if palette_map_entry is None:
                # Create a new entry in the palette map for new block-state combos.
                palette_map_entry = StructurePaletteEntry(
                    index=len(palette_map), block=block
                )
                palette_map[palette_map_key] = palette_map_entry
            # Create and append a new block entry using the palette entry's index.
            output_block_entry = StructureBlockEntry(
                state=palette_map_entry.index,
                pos=actual_pos,
            )
            # Note NBT is part of the block entry, not the palette.
            if block.data:
                output_block_entry.nbt = block.data
            blocks.append(output_block_entry)

        # Convert the palette map into the final palette, sorted by index.
        palette = sorted(palette_map.values(), key=lambda entry: entry.index)

        # Create and return the final output structure.
        return StructureData(
            size=self.actual_size,
            palette=palette,
            blocks=blocks,
        )
