import string
from collections import defaultdict
from dataclasses import dataclass
from typing import ClassVar, DefaultDict, Iterable, Iterator, Literal, Optional

from mcblueprints.lib.block import Block
from mcblueprints.lib.structure_data import (
    StructureBlockEntry,
    StructureData,
    StructurePaletteEntry,
)
from mcblueprints.lib.vec import Vec3

__all__ = ["BlockMap"]


@dataclass
class BlockMap:
    size: Vec3 | Literal["auto"]

    # y -> x -> z
    block_map: DefaultDict[int, DefaultDict[int, dict[int, Block]]]

    SYMBOLS: ClassVar[str] = string.digits + string.ascii_letters

    def __init__(self, size: Vec3 | Literal["auto"]):
        self.size = size
        self.block_map = defaultdict(lambda: defaultdict(dict))

    def __str__(self) -> str:
        return self.to_ascii()

    def __setitem__(self, key: Vec3, value: Block):
        x, y, z = key
        if not self._in_bounds(x, y, z):
            raise ValueError(
                f"Position ({x}, {y}, {z}) exceeds block map size ({self.size})"
            )
        self.block_map[y][x][z] = value

    def __getitem__(self, key: Vec3) -> Block:
        x, y, z = key
        return self.block_map[y][x][z]

    def __delitem__(self, key: Vec3):
        x, y, z = key
        del self.block_map[y][x][z]

    def __iter__(self) -> Iterator[tuple[Vec3, Block]]:
        for y, layer in self.block_map.items():
            for x, row in layer.items():
                for z, block in row.items():
                    yield (x, y, z), block

    def _in_bounds(self, x: int, y: int, z: int) -> bool:
        if self.size == "auto":
            return True
        size_x, size_y, size_z = self.size
        return (x < size_x) and (y < size_y) and (z < size_z)

    @property
    def actual_size(self) -> tuple[int, int, int]:
        if self.size != "auto":
            return self.size

        positions = ((x, y, z) for (x, y, z), _ in self)
        first_position = next(positions, None)

        if not first_position:
            return (0, 0, 0)

        first_x, first_y, first_z = first_position
        x_max, x_min = first_x, first_x
        y_max, y_min = first_y, first_y
        z_max, z_min = first_z, first_z

        for (x, y, z) in positions:
            x_max, x_min = max(x_max, x), min(x_min, x)
            y_max, y_min = max(y_max, y), min(y_min, y)
            z_max, z_min = max(z_max, z), min(z_min, z)

        size_x = 1 + x_max - x_min
        size_y = 1 + y_max - y_min
        size_z = 1 + z_max - z_min

        return (size_x, size_y, size_z)

    def get(self, key: Vec3) -> Optional[Block]:
        x, y, z = key
        row = self.block_map[y][x]
        return row.get(z)

    def remove_blocks(self, blocks: list[Block]):
        for position, block in self:
            if block.matches_any_of(blocks):
                del self[position]
                continue

    def keep_blocks(self, blocks: list[Block]):
        positions_to_remove: list[Vec3] = []
        # Collect positions to remove first because we can't mutate during iteration.
        for position, block in self:
            if block.matches_any_of(blocks):
                continue
            positions_to_remove.append(position)
        for position in positions_to_remove:
            del self[position]

    def replace_blocks(self, blocks: list[Block], replacement: Block):
        for position, block in self:
            if block.matches_any_of(blocks):
                self[position] = replacement
                continue

    def scan(self, block: Block) -> Iterable[Vec3]:
        yield from (position for position, b in self if b == block)

    def merge(self, other: "BlockMap", position: Optional[Vec3] = None):
        position = position or (0, 0, 0)
        for offset, block in other:
            new_pos = (
                position[0] + offset[0],
                position[1] + offset[1],
                position[2] + offset[2],
            )
            self[new_pos] = block

    def to_ascii(self) -> str:
        next_symbol_index = 0
        symbol_by_block: dict[Block, str] = {}
        layers: list[str] = []
        size_x, size_y, size_z = self.actual_size
        for y in range(size_y):
            rows: list[str] = []
            for x in range(size_x):
                line: str = ""
                for z in range(size_z):
                    block = self.get((x, y, z))
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
        for position, block in self:
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
                pos=position,
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
