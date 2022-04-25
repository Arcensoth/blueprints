# FIXME

from typing import Any, Callable, Dict, List, Optional, cast

from pyckaxe import HERE, Block, Breadcrumb, Position, ResourceLink, ResourceLocation

from mcblueprints.lib.blueprint.blueprint import (
    Blueprint,
    BlueprintLayout,
    BlueprintPalette,
    BlueprintPaletteEntry,
)
from mcblueprints.lib.filter.filter import Filter
from mcblueprints.lib.filter.filter_deserializer import FilterDeserializer
from mcblueprints.lib.material.material import Material
from mcblueprints.lib.material.material_deserializer import MaterialDeserializer

__all__ = ("BlueprintDeserializer",)


class BlueprintDeserializationException(Exception):
    pass


class MalformedBlueprint(BlueprintDeserializationException):
    def __init__(self, message: str, raw_blueprint: Any, breadcrumb: Breadcrumb):
        self.raw_blueprint: Any = raw_blueprint
        self.breadcrumb: Breadcrumb = breadcrumb
        super().__init__(message)


class MalformedPaletteEntry(BlueprintDeserializationException):
    def __init__(self, message: str, raw_palette_entry: Any, breadcrumb: Breadcrumb):
        self.raw_palette_entry: Any = raw_palette_entry
        self.breadcrumb: Breadcrumb = breadcrumb
        super().__init__(message)


# @implements ResourceDeserializer[Blueprint, Any]
class BlueprintDeserializer:
    # @implements ResourceDeserializer
    def __call__(self, raw: Any, **kwargs) -> Blueprint:
        return Blueprint.parse_obj(raw)

    def deserialize_palette(
        self, raw_palette: Any, breadcrumb: Breadcrumb
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

    def deserialize_layout(
        self, raw_layout: Any, breadcrumb: Breadcrumb
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
