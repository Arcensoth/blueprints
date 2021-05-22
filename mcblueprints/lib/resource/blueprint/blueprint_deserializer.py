from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, cast

from pyckaxe import HERE, Block, Breadcrumb, JsonValue, Position, ResourceLocation

from mcblueprints.lib.resource.blueprint.blueprint import (
    Blueprint,
    BlueprintLayout,
    BlueprintPalette,
)
from mcblueprints.lib.resource.blueprint.palette_entry.abc.blueprint_palette_entry import (
    BlueprintPaletteEntry,
)
from mcblueprints.lib.resource.blueprint.palette_entry.block_blueprint_palette_entry import (
    BlockBlueprintPaletteEntry,
)
from mcblueprints.lib.resource.blueprint.palette_entry.blueprint_blueprint_palette_entry import (
    BlueprintBlueprintPaletteEntry,
)
from mcblueprints.lib.resource.blueprint.palette_entry.material_blueprint_palette_entry import (
    MaterialBlueprintPaletteEntry,
)
from mcblueprints.lib.resource.blueprint.palette_entry.void_blueprint_palette_entry import (
    VoidBlueprintPaletteEntry,
)
from mcblueprints.lib.resource.blueprint.types import BlueprintOrLocation
from mcblueprints.lib.resource.filter.filter_deserializer import FilterDeserializer
from mcblueprints.lib.resource.filter.types import FilterOrLocation
from mcblueprints.lib.resource.material.material import Material
from mcblueprints.lib.resource.material.material_deserializer import (
    MaterialDeserializer,
)

__all__ = ("BlueprintDeserializer",)


class BlueprintDeserializationException(Exception):
    pass


class MalformedBlueprint(BlueprintDeserializationException):
    def __init__(self, message: str, raw_blueprint: JsonValue, breadcrumb: Breadcrumb):
        self.raw_blueprint: JsonValue = raw_blueprint
        self.breadcrumb: Breadcrumb = breadcrumb
        super().__init__(message)


class MalformedPaletteEntry(BlueprintDeserializationException):
    def __init__(
        self, message: str, raw_palette_entry: JsonValue, breadcrumb: Breadcrumb
    ):
        self.raw_palette_entry: JsonValue = raw_palette_entry
        self.breadcrumb: Breadcrumb = breadcrumb
        super().__init__(message)


# @implements ResourceDeserializer[JsonValue, Blueprint]
@dataclass
class BlueprintDeserializer:
    filter_deserializer: FilterDeserializer
    material_deserializer: MaterialDeserializer

    palette_entry_deserializers: Dict[
        str, Callable[[str, Dict[str, JsonValue], Breadcrumb], BlueprintPaletteEntry]
    ] = field(init=False)

    def __post_init__(self):
        self.palette_entry_deserializers = {
            "block": self.deserialize_block_palette_entry,
            "blueprint": self.deserialize_blueprint_palette_entry,
            "material": self.deserialize_material_palette_entry,
            "void": self.deserialize_void_palette_entry,
        }

    # @implements ResourceDeserializer
    def __call__(
        self,
        raw: JsonValue,
        *,
        breadcrumb: Optional[Breadcrumb] = None,
    ) -> Blueprint:
        return self.deserialize(raw, breadcrumb or Breadcrumb())

    def or_location(
        self, raw: JsonValue, breadcrumb: Breadcrumb
    ) -> BlueprintOrLocation:
        """Deserialize a `Blueprint` or `BlueprintLocation` from a raw value."""
        # A string is assumed to be a resource location.
        if isinstance(raw, str):
            return Blueprint @ ResourceLocation.from_string(raw)
        # Anything else is assumed to be a serialized resource.
        return self(raw, breadcrumb=breadcrumb)

    def deserialize(
        self, raw_blueprint: JsonValue, breadcrumb: Breadcrumb
    ) -> Blueprint:
        """Deserialize a `Blueprint` from a raw value."""
        if not isinstance(raw_blueprint, dict):
            raise MalformedBlueprint(
                f"Malformed blueprint, at `{breadcrumb}`", raw_blueprint, breadcrumb
            )

        # size (required, non-nullable)
        raw_size = raw_blueprint.get("size")
        breadcrumb_size = breadcrumb.size
        if raw_size is None:
            raise MalformedBlueprint(
                f"Missing `size`, at `{breadcrumb_size}`",
                raw_blueprint,
                breadcrumb_size,
            )
        size = self.deserialize_size(raw_size, breadcrumb_size)

        # anchor (optional, non-nullable, has a default)
        anchor: Position = HERE
        if raw_anchor := raw_blueprint.get("anchor"):
            anchor = self.deserialize_anchor(raw_anchor, breadcrumb.anchor)

        # palette (required, non-nullable)
        raw_palette = raw_blueprint.get("palette")
        breadcrumb_palette = breadcrumb.palette
        if raw_palette is None:
            raise MalformedBlueprint(
                f"Missing `palette`, at `{breadcrumb_palette}`",
                raw_blueprint,
                breadcrumb_palette,
            )
        palette = self.deserialize_palette(raw_palette, breadcrumb_palette)

        # layout (required, non-nullable)
        raw_layout = raw_blueprint.get("layout")
        breadcrumb_layout = breadcrumb.layout
        if raw_layout is None:
            raise MalformedBlueprint(
                f"Missing `layout`, at `{breadcrumb_layout}`",
                raw_blueprint,
                breadcrumb_layout,
            )
        layout = self.deserialize_layout(raw_layout, breadcrumb_layout)

        blueprint = Blueprint(
            size=size,
            anchor=anchor,
            palette=palette,
            layout=layout,
        )

        return blueprint

    def deserialize_size(self, raw_size: JsonValue, breadcrumb: Breadcrumb) -> Position:
        if not isinstance(raw_size, list):
            raise MalformedBlueprint(
                f"Malformed `size`, at `{breadcrumb}`", raw_size, breadcrumb
            )
        return ~Position.from_list(cast(Any, raw_size))

    def deserialize_anchor(
        self, raw_anchor: JsonValue, breadcrumb: Breadcrumb
    ) -> Position:
        if not isinstance(raw_anchor, list):
            raise MalformedBlueprint(
                f"Malformed `anchor`, at `{breadcrumb}`", raw_anchor, breadcrumb
            )
        return ~Position.from_list(cast(Any, raw_anchor))

    def deserialize_palette(
        self, raw_palette: JsonValue, breadcrumb: Breadcrumb
    ) -> BlueprintPalette:
        if not isinstance(raw_palette, dict):
            raise MalformedBlueprint(
                f"Malformed `palette`, at `{breadcrumb}`", raw_palette, breadcrumb
            )
        palette: Dict[str, BlueprintPaletteEntry] = {}
        for i, (palette_key, raw_palette_entry) in enumerate(raw_palette.items()):
            if len(palette_key) != 1:
                raise MalformedPaletteEntry(
                    f"Palette key `{palette_key}` is not a single character,"
                    + f" at `{breadcrumb[palette_key]}`",
                    raw_palette_entry,
                    breadcrumb[palette_key],
                )
            palette[palette_key] = self.deserialize_palette_entry(
                palette_key, raw_palette_entry, breadcrumb[i]
            )
        return palette

    def deserialize_palette_entry(
        self, palette_key: str, raw_palette_entry: JsonValue, breadcrumb: Breadcrumb
    ) -> BlueprintPaletteEntry:
        # A string is assumed to be a basic block.
        if isinstance(raw_palette_entry, str):
            material = Material(block=Block(name=raw_palette_entry))
            return MaterialBlueprintPaletteEntry(key=palette_key, material=material)

        # Otherwise we ought to have a concrete definition...

        if not isinstance(raw_palette_entry, dict):
            raise MalformedPaletteEntry(
                f"Malformed palette entry, at `{breadcrumb}`",
                raw_palette_entry,
                breadcrumb,
            )

        palette_entry_type = raw_palette_entry.get("type")
        breadcrumb_type = breadcrumb.type
        if palette_entry_type is None:
            raise MalformedPaletteEntry(
                f"Missing `type`, at `{breadcrumb_type}`",
                raw_palette_entry,
                breadcrumb_type,
            )
        if not isinstance(palette_entry_type, str):
            raise MalformedPaletteEntry(
                f"Malformed `type`, at `{breadcrumb_type}`",
                raw_palette_entry,
                breadcrumb_type,
            )

        palette_entry_deserializer = self.palette_entry_deserializers.get(
            palette_entry_type
        )

        if not palette_entry_deserializer:
            raise MalformedPaletteEntry(
                f"Unknown type `{palette_entry_type}`, at `{breadcrumb_type}`",
                raw_palette_entry,
                breadcrumb,
            )

        palette_entry = palette_entry_deserializer(
            palette_key, raw_palette_entry, breadcrumb
        )

        return palette_entry

    def deserialize_block_palette_entry(
        self,
        palette_key: str,
        raw_palette_entry: Dict[str, JsonValue],
        breadcrumb: Breadcrumb,
    ) -> BlockBlueprintPaletteEntry:
        block = self.material_deserializer.deserialize_block(
            raw_palette_entry, breadcrumb
        )
        return BlockBlueprintPaletteEntry(key=palette_key, block=block)

    def deserialize_blueprint_palette_entry(
        self,
        palette_key: str,
        raw_palette_entry: Dict[str, JsonValue],
        breadcrumb: Breadcrumb,
    ) -> BlueprintBlueprintPaletteEntry:
        # blueprint (required, non-nullable)
        raw_blueprint = raw_palette_entry.get("blueprint")
        breadcrumb_blueprint = breadcrumb.blueprint
        if raw_blueprint is None:
            raise MalformedPaletteEntry(
                f"Missing `blueprint`, at `{breadcrumb_blueprint}`",
                raw_palette_entry,
                breadcrumb_blueprint,
            )
        blueprint = self.or_location(raw_blueprint, breadcrumb_blueprint)

        # offset (optional, non-nullable, has a default)
        offset: Position = HERE
        if raw_offset := raw_palette_entry.get("offset"):
            if not isinstance(raw_offset, list):
                raise MalformedBlueprint(
                    f"Malformed `offset`, at `{breadcrumb.offset}`",
                    raw_offset,
                    breadcrumb.offset,
                )
            offset = ~Position.from_list(cast(Any, raw_offset))

        # filter (optional, nullable, defaults to null)
        filter: Optional[FilterOrLocation] = None
        if raw_filter := raw_palette_entry.get("filter"):
            filter = self.filter_deserializer.or_location(raw_filter, breadcrumb.filter)

        return BlueprintBlueprintPaletteEntry(
            key=palette_key, blueprint=blueprint, offset=offset, filter=filter
        )

    def deserialize_material_palette_entry(
        self,
        palette_key: str,
        raw_palette_entry: Dict[str, JsonValue],
        breadcrumb: Breadcrumb,
    ) -> MaterialBlueprintPaletteEntry:
        # material (required, non-nullable)
        raw_material = raw_palette_entry.get("material")
        if raw_material is None:
            raise MalformedPaletteEntry(
                f"Missing `material`, at `{breadcrumb.material}`",
                raw_palette_entry,
                breadcrumb.material,
            )
        material = self.material_deserializer.or_location(raw_material, breadcrumb)

        return MaterialBlueprintPaletteEntry(key=palette_key, material=material)

    def deserialize_void_palette_entry(
        self,
        palette_key: str,
        raw_palette_entry: Dict[str, JsonValue],
        breadcrumb: Breadcrumb,
    ) -> VoidBlueprintPaletteEntry:
        return VoidBlueprintPaletteEntry(key=palette_key)

    def deserialize_layout(
        self, raw_layout: JsonValue, breadcrumb: Breadcrumb
    ) -> BlueprintLayout:
        if not isinstance(raw_layout, list):
            raise MalformedBlueprint(
                f"Malformed `layout`, at `{breadcrumb}`", raw_layout, breadcrumb
            )

        layout: BlueprintLayout = []

        # Read the layout upside-down.
        for i, raw_layer in enumerate(reversed(raw_layout)):
            if raw_layer is None:
                layout.append([])
                continue

            if isinstance(raw_layer, str):
                raw_layer = list(raw_layer)

            if not isinstance(raw_layer, list):
                raise MalformedBlueprint(
                    f"Malformed `layout` layer, at `{breadcrumb[i]}`",
                    raw_layer,
                    breadcrumb[i],
                )

            layer: List[str] = []

            for j, raw_row in enumerate(raw_layer):
                if raw_row is None:
                    layer.append("")
                    continue

                if not isinstance(raw_row, str):
                    raise MalformedBlueprint(
                        f"Malformed `layout` row, at `{breadcrumb[i][j]}`",
                        raw_row,
                        breadcrumb[i][j],
                    )

                layer.append(raw_row)

            layout.append(layer)

        return layout
