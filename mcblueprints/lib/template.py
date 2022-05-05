from typing import Annotated, Any, Iterable, Literal, Optional, Union, cast

from beet import Context, FileDeserialize, JsonFileBase
from pydantic import BaseModel, Field, validator

from mcblueprints.lib.block import Block
from mcblueprints.lib.block_map import BlockMap
from mcblueprints.lib.block_provider import BlockProvider
from mcblueprints.lib.filter import FilterLink
from mcblueprints.lib.normalizable_model import NormalizableModel
from mcblueprints.lib.structure_data import StructureData
from mcblueprints.lib.template_variable import TemplateVariable
from mcblueprints.lib.vec import Vec3

__all__ = ["Template", "TemplateLink", "TemplateFile"]


class TemplatePaletteEntry(NormalizableModel):
    __root__: Annotated[
        Union[
            "VoidTemplatePaletteEntry",
            "BlockTemplatePaletteEntry",
            "BlockProviderTemplatePaletteEntry",
            "TemplateTemplatePaletteEntry",
        ],
        Field(discriminator="type"),
    ]

    @classmethod
    def normalize_input(cls, value: Any) -> Any:
        if isinstance(value, str):
            return dict(type="block_provider", provider=value)
        return value

    def merge(self, ctx: Context, block_map: BlockMap, position: Vec3):
        self.__root__.merge(ctx, block_map, position)


class VoidTemplatePaletteEntry(BaseModel):
    type: Literal["void"]

    def merge(self, ctx: Context, block_map: BlockMap, position: Vec3):
        # Void the block in the block map.
        del block_map[position]


class BlockTemplatePaletteEntry(BaseModel):
    type: Literal["block"]

    block: Block

    def merge(self, ctx: Context, block_map: BlockMap, position: Vec3):
        # Set the corresponding block in the block map.
        block_map[position] = self.block


class BlockProviderTemplatePaletteEntry(BaseModel):
    type: Literal["block_provider"]

    provider: BlockProvider

    def merge(self, ctx: Context, block_map: BlockMap, position: Vec3):
        # Resolve the block from the provider.
        block = self.provider(ctx)
        # Set the corresponding block in the block map.
        block_map[position] = block


class TemplateTemplatePaletteEntry(BaseModel):
    type: Literal["template"]

    template: "TemplateLink"
    offset: Vec3 = Field(default_factory=lambda: (0, 0, 0))
    variables: dict[str, BlockProvider] = Field(default_factory=dict)
    filter: Optional[FilterLink] = None

    def merge(self, ctx: Context, block_map: BlockMap, position: Vec3):
        # Resolve the child template.
        child_template = self.template(ctx)

        # Flatten the child template into its own block map independently.
        child_block_map = child_template.to_block_map(ctx)

        # If any variables have been provided, expand them immediately.
        if self.variables:
            for variable, elem in self.variables.items():
                variable_block = TemplateVariable(name=variable).to_block()
                replacement_block = elem(ctx)
                child_block_map.replace_blocks([variable_block], replacement_block)

        # If a filter is present, apply it to the child block map before merging it.
        if self.filter is not None:
            filter = self.filter(ctx)
            filter.__root__.apply(ctx, child_block_map)

        # Merge the converted child block map into the parent block map.
        child_offset = (
            position[0] - self.offset[0] - child_template.anchor[0],
            position[1] - self.offset[1] - child_template.anchor[1],
            position[2] - self.offset[2] - child_template.anchor[2],
        )
        block_map.merge(child_block_map, child_offset)


class TemplateLayout(BaseModel):
    __root__: list[list[str]]

    @validator("__root__", pre=True)
    def root_in_reverse(cls, value: Any):
        if not isinstance(value, list):
            raise ValueError(f"Expected layout to be a `str` but got: f{value}")

        raw_layout = cast(list[Any], value)

        layout: list[list[str]] = []

        # Read the layout upside-down.
        for i, raw_layer in enumerate(reversed(raw_layout)):
            if raw_layer is None:
                layout.append([])
                continue

            if isinstance(raw_layer, str):
                raw_layer = list(raw_layer)

            if not isinstance(raw_layer, list):
                raise ValueError(
                    f"Expected layer {i} to be a `str` or `list`, but got: {raw_layer}"
                )

            raw_layer = cast(list[Any], raw_layer)

            layer: list[str] = []

            for j, raw_row in enumerate(raw_layer):
                if raw_row is None:
                    layer.append("")
                    continue

                if not isinstance(raw_row, str):
                    raise ValueError(
                        f"Expected row {j} in layer {i} to be a `str`, but got: {raw_row}"
                    )

                layer.append(raw_row)

            layout.append(layer)

        return layout


class Template(BaseModel):
    size: Vec3 | Literal["auto"] = "auto"
    anchor: Vec3 = Field(default_factory=lambda: (0, 0, 0))
    palette: dict[str, TemplatePaletteEntry] = Field(default_factory=dict)
    layout: TemplateLayout = Field(default_factory=lambda: TemplateLayout(__root__=[]))

    def scan(self, symbol: str) -> Iterable[Vec3]:
        """Scan over the layout, looking for a particular symbol."""
        for y, floor in enumerate(self.layout.__root__):
            for x, row in enumerate(floor):
                yield from ((x, y, z) for z, s in enumerate(row) if s == symbol)

    def to_block_map(self, ctx: Context) -> BlockMap:
        # Create a new block map to hold the final state.
        block_map = BlockMap(size=self.size)
        # Traverse palette entries in the order they are defined.
        for palette_key, palette_entry in self.palette.items():
            # Scan over the layout once per entry, looking for matching symbols.
            for offset in self.scan(palette_key):
                # Merge the palette entry into the block map at the offset.
                palette_entry.merge(ctx, block_map, offset)
        return block_map

    def to_structure_data(self, ctx: Context) -> StructureData:
        # Flatten the template into a block map, and turn that into a structure.
        block_map = self.to_block_map(ctx)
        return block_map.to_structure_data()


class TemplateLink(BaseModel):
    __root__: str | Template

    def __call__(self, ctx: Context) -> Template:
        if isinstance(self.__root__, str):
            return ctx.data[TemplateFile][self.__root__].data
        return self.__root__


TemplateTemplatePaletteEntry.update_forward_refs()
TemplatePaletteEntry.update_forward_refs()


class TemplateFile(JsonFileBase[Template]):
    scope = ("blueprints", "templates")
    extension = ".json"
    model = Template
    data: FileDeserialize[Template] = FileDeserialize()
