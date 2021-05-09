from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set, cast

from pyckaxe.lib import JsonValue, Position, ResourceLocation
from pyckaxe.lib.block import Block

from blueprints.lib.resource.blueprint.blueprint import (
    Blueprint,
    BlueprintLayout,
    BlueprintSymbolMap,
)
from blueprints.lib.resource.blueprint.palette_entry.abc.blueprint_palette_entry import (
    BlueprintPalette,
    BlueprintPaletteEntry,
)
from blueprints.lib.resource.blueprint.palette_entry.blueprint_blueprint_palette_entry import (
    BlueprintBlueprintPaletteEntry,
)
from blueprints.lib.resource.blueprint.palette_entry.material_blueprint_palette_entry import (
    MaterialBlueprintPaletteEntry,
)
from blueprints.lib.resource.blueprint.palette_entry.void_blueprint_palette_entry import (
    VoidBlueprintPaletteEntry,
)
from blueprints.lib.resource.blueprint.types import BlueprintOrLocation
from blueprints.lib.resource.material.material import Material
from blueprints.lib.resource.material.material_deserializer import MaterialDeserializer
from blueprints.lib.resource.material.types import MaterialOrLocation

__all__ = ("BlueprintDeserializer",)


class BlueprintDeserializationException(Exception):
    pass


class MalformedBlueprint(BlueprintDeserializationException):
    def __init__(self, raw: JsonValue):
        self.raw: JsonValue = raw
        super().__init__(f"Malformed blueprint")


class MissingSize(BlueprintDeserializationException):
    def __init__(self, raw: JsonValue):
        self.raw: JsonValue = raw
        super().__init__(f"Missing size")


class InvalidSize(BlueprintDeserializationException):
    def __init__(self, raw_size: JsonValue):
        self.raw_size = raw_size
        super().__init__(f"Invalid size: {raw_size}")


class MissingPalette(BlueprintDeserializationException):
    def __init__(self, raw: JsonValue):
        self.raw: JsonValue = raw
        super().__init__(f"Missing palette")


class UnknownPaletteEntryType(BlueprintDeserializationException):
    def __init__(self, raw_type: str):
        self.raw_type: str = raw_type
        super().__init__(f"Unknown palette entry type: {raw_type}")


class InvalidPalette(BlueprintDeserializationException):
    def __init__(self, raw_palette: JsonValue):
        self.raw_palette = raw_palette
        super().__init__(f"Invalid palette: {raw_palette}")


class MissingSymbols(BlueprintDeserializationException):
    def __init__(self, raw: JsonValue):
        self.raw: JsonValue = raw
        super().__init__(f"Missing symbols")


class InvalidSymbols(BlueprintDeserializationException):
    def __init__(self, raw_symbols: JsonValue):
        self.raw_symbols = raw_symbols
        super().__init__(f"Invalid symbols: {raw_symbols}")


class MissingLayout(BlueprintDeserializationException):
    def __init__(self, raw: JsonValue):
        self.raw: JsonValue = raw
        super().__init__(f"Missing layout")


class InvalidLayout(BlueprintDeserializationException):
    def __init__(self, raw_layout: JsonValue):
        self.raw_layout = raw_layout
        super().__init__(f"Invalid layout: {raw_layout}")


class InvalidStructurePivot(BlueprintDeserializationException):
    def __init__(self, raw_structure_pivot: JsonValue):
        self.raw_structure_pivot = raw_structure_pivot
        super().__init__(f"Invalid structure pivot: {raw_structure_pivot}")


class InvalidResidueMask(BlueprintDeserializationException):
    def __init__(self, raw_residue_mask: JsonValue):
        self.raw_residue_mask = raw_residue_mask
        super().__init__(f"Invalid residue mask: {raw_residue_mask}")


# @implements ResourceDeserializer[JsonValue, Blueprint]
@dataclass
class BlueprintDeserializer:
    material_deserializer: MaterialDeserializer

    # @implements ResourceDeserializer
    def __call__(self, raw: JsonValue) -> Blueprint:
        return self.deserialize(raw)

    def or_location(self, raw: JsonValue) -> BlueprintOrLocation:
        """ Deserialize a blueprint or location from a raw value. """
        # A string is assumed to be a resource location.
        if isinstance(raw, str):
            return Blueprint @ ResourceLocation.from_string(raw)
        # Anything else is assumed to be a serialized resource.
        return self(raw)

    def deserialize(self, raw: JsonValue) -> Blueprint:
        """ Deserialize a `Blueprint` from a raw value. """
        try:
            if not isinstance(raw, dict):
                raise MalformedBlueprint(raw)

            raw_size = raw.get("size")
            if raw_size is None:
                raise MissingSize(raw)
            size = self.deserialize_size(raw_size)

            raw_palette = raw.get("palette")
            if raw_palette is None:
                raise MissingPalette(raw)
            palette = self.deserialize_palette(raw_palette)

            raw_symbols = raw.get("symbols")
            if raw_symbols is None:
                raise MissingSymbols(raw)
            symbols = self.deserialize_symbols(raw_symbols)

            raw_layout = raw.get("layout")
            if raw_layout is None:
                raise MissingLayout(raw)
            layout = self.deserialize_layout(raw_layout)

            raw_structure_pivot = raw.get("structure_pivot")
            structure_pivot = self.deserialize_structure_pivot(raw_structure_pivot)

            raw_residue_mask = raw.get("residue_mask")
            residue_mask = self.deserialize_residue_mask(raw_residue_mask)

            return Blueprint(
                size=size,
                structure_pivot=structure_pivot,
                residue_mask=residue_mask,
                palette=palette,
                symbols=symbols,
                layout=layout,
            )

        except BlueprintDeserializationException as ex:
            raise ex

        except Exception as ex:
            raise MalformedBlueprint(raw) from ex

    def deserialize_size(self, raw_size: JsonValue) -> Position:
        try:
            position = ~Position.from_list(cast(Any, raw_size))
            return position
        except Exception as ex:
            raise InvalidSize(raw_size) from ex

    def deserialize_palette(self, raw_palette: JsonValue) -> BlueprintPalette:
        try:
            assert isinstance(raw_palette, dict)
            palette = {
                palette_key: self.deserialize_palette_entry(
                    palette_key, raw_palette_entry
                )
                for palette_key, raw_palette_entry in raw_palette.items()
            }
            return palette
        except Exception as ex:
            raise InvalidPalette(raw_palette) from ex

    def deserialize_palette_entry(
        self, palette_key: str, raw_palette_entry: JsonValue
    ) -> BlueprintPaletteEntry:
        # A string is assumed to be a basic block.
        if isinstance(raw_palette_entry, str):
            block_name = raw_palette_entry
            material = Material(Block(block_name))
            return MaterialBlueprintPaletteEntry(key=palette_key, material=material)
        # Otherwise we ought to have a concrete definition.
        assert isinstance(raw_palette_entry, dict)
        raw_type = raw_palette_entry.get("type")
        assert isinstance(raw_type, str)
        palette_entry_deserializers: Dict[
            str, Callable[[str, JsonValue], BlueprintPaletteEntry]
        ] = {
            "blueprint": self.deserialize_blueprint_palette_entry,
            "material": self.deserialize_material_palette_entry,
            "void": self.deserialize_void_palette_entry,
        }
        palette_entry_deserializer = palette_entry_deserializers.get(raw_type)
        if not palette_entry_deserializer:
            raise UnknownPaletteEntryType(raw_type)
        palette_entry = palette_entry_deserializer(palette_key, raw_palette_entry)
        return palette_entry

    def deserialize_blueprint_palette_entry(
        self, palette_key: str, raw_palette_entry: JsonValue
    ) -> BlueprintBlueprintPaletteEntry:
        assert isinstance(raw_palette_entry, dict)

        raw_blueprint = raw_palette_entry.get("blueprint")
        assert raw_blueprint is not None
        blueprint = self.or_location(raw_blueprint)

        raw_offset = raw_palette_entry.get("offset", [0, 0, 0])
        offset = ~Position.from_list(cast(Any, raw_offset))

        filter_keys: Set[str] = set()
        raw_filter_keys = raw_palette_entry.get("filter_keys")
        if raw_filter_keys is not None:
            assert isinstance(raw_filter_keys, list)
            for filter_key in raw_filter_keys:
                assert isinstance(filter_key, str)
                assert filter_key not in filter_keys
                filter_keys.add(filter_key)

        replace_keys: Dict[str, str] = {}
        raw_replace_keys = raw_palette_entry.get("replace_keys")
        if raw_replace_keys is not None:
            assert isinstance(raw_replace_keys, dict)
            for k, v in raw_replace_keys.items():
                assert isinstance(v, str)
                replace_keys[k] = v

        return BlueprintBlueprintPaletteEntry(
            key=palette_key,
            blueprint=blueprint,
            offset=offset,
            filter_keys=filter_keys,
            replace_keys=replace_keys,
        )

    def deserialize_material_palette_entry(
        self, palette_key: str, raw_palette_entry: JsonValue
    ) -> MaterialBlueprintPaletteEntry:
        assert isinstance(raw_palette_entry, dict)
        raw_material = raw_palette_entry.get("material")
        assert raw_material is not None
        material = self.material_deserializer.or_location(raw_material)
        return MaterialBlueprintPaletteEntry(
            key=palette_key,
            material=material,
        )

    def deserialize_void_palette_entry(
        self, palette_key: str, raw_palette_entry: JsonValue
    ) -> VoidBlueprintPaletteEntry:
        return VoidBlueprintPaletteEntry(
            key=palette_key,
        )

    def deserialize_symbols(self, raw_symbols: JsonValue) -> BlueprintSymbolMap:
        try:
            assert isinstance(raw_symbols, dict)
            symbols = cast(BlueprintSymbolMap, raw_symbols)
            return symbols
        except Exception as ex:
            raise InvalidSymbols(raw_symbols) from ex

    def deserialize_layout(self, raw_layout: JsonValue) -> BlueprintLayout:
        try:
            assert isinstance(raw_layout, list)

            layout: BlueprintLayout = []

            # Read the layout upside-down.
            for raw_layer in reversed(raw_layout):
                if raw_layer is None:
                    layout.append([])
                    continue

                if isinstance(raw_layer, str):
                    raw_layer = list(raw_layer)

                assert isinstance(raw_layer, list)

                layer: List[str] = []

                for raw_row in raw_layer:
                    if raw_row is None:
                        layer.append("")
                        continue
                    assert isinstance(raw_row, str)
                    layer.append(raw_row)

                layout.append(layer)

            return layout

        except Exception as ex:
            raise InvalidLayout(raw_layout) from ex

    def deserialize_structure_pivot(
        self, raw_structure_pivot: JsonValue
    ) -> Optional[Position]:
        if raw_structure_pivot is not None:
            try:
                return Position.from_list(cast(Any, raw_structure_pivot))
            except Exception as ex:
                raise InvalidStructurePivot(raw_structure_pivot) from ex

    def deserialize_residue_mask(
        self, raw_residue_mask: JsonValue
    ) -> Optional[MaterialOrLocation]:
        if raw_residue_mask is not None:
            try:
                return self.material_deserializer.or_location(raw_residue_mask)
            except Exception as ex:
                raise InvalidResidueMask(raw_residue_mask) from ex
