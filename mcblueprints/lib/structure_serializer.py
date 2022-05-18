from dataclasses import dataclass
from typing import Any

from mcblueprints.lib.structure_data import (
    StructureBlockEntry,
    StructureData,
    StructureEntityEntry,
    StructurePaletteEntry,
)
from mcblueprints.lib.types import Vec3
from mcblueprints.utils.nbt import StructureFileData


@dataclass(frozen=True)
class StructureSerializer:
    data_version: int

    def __call__(self, data: StructureData) -> StructureFileData:
        return self.serialize(data)

    def serialize(self, data: StructureData) -> StructureFileData:
        return StructureFileData(
            {
                "DataVersion": self.data_version,
                "size": self.serialize_size(data.size),
                "palette": self.serialize_palette(data.palette),
                "blocks": self.serialize_blocks(data.blocks),
                "entities": self.serialize_entities(data.entities),
            }
        )

    def serialize_size(self, size: Vec3) -> Any:
        return [int(c) for c in size]

    def serialize_palette(self, palette: list[StructurePaletteEntry]) -> Any:
        serialized_palette: list[Any] = []
        for palette_entry in palette:
            serialized_palette_entry: dict[str, Any] = {
                "Name": palette_entry.block.name,
            }
            if palette_entry.block.state:
                block_state_nbt = palette_entry.block.state.to_nbt()
                serialized_palette_entry["Properties"] = block_state_nbt
            serialized_palette.append(serialized_palette_entry)
        return serialized_palette

    def serialize_blocks(self, blocks: list[StructureBlockEntry]) -> Any:
        serialized_blocks: list[Any] = []
        for block_entry in blocks:
            serialized_block_entry: dict[str, Any] = {
                "state": block_entry.state,
                "pos": [int(c) for c in block_entry.pos],
            }
            if block_entry.nbt:
                serialized_block_entry["nbt"] = block_entry.nbt
            serialized_blocks.append(serialized_block_entry)
        return serialized_blocks

    def serialize_entities(self, entities: list[StructureEntityEntry]) -> Any:
        return [
            {
                "pos": [float(c) for c in entity_entry.pos],
                "blockPos": [int(c) for c in entity_entry.pos],
                "nbt": entity_entry.nbt,
            }
            for entity_entry in entities
        ]
