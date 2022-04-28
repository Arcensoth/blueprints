from typing import Annotated, Any, Literal, Union

from beet import Context, FileDeserialize, JsonFileBase
from pydantic import BaseModel, Field

from mcblueprints.lib.block_map import BlockMap
from mcblueprints.lib.block_provider import BlockProvider
from mcblueprints.lib.normalizable_model import NormalizableModel

__all__ = ["Filter", "FilterLink", "FilterFile"]


class Filter(NormalizableModel):
    __root__: Annotated[
        Union[
            "GroupFilter",
            "KeepFilter",
            "RemoveFilter",
            "ReplaceFilter",
        ],
        Field(discriminator="type"),
    ]

    @classmethod
    def normalize_input(cls, value: Any) -> Any:
        if isinstance(value, list):
            return dict(type="group", children=value)  # type: ignore
        return value


class FilterLink(BaseModel):
    __root__: str | Filter

    def __call__(self, ctx: Context) -> Filter:
        if isinstance(self.__root__, str):
            return ctx.data[FilterFile][self.__root__].data
        return self.__root__


class FilterFile(JsonFileBase[Filter]):
    scope = ("blueprints", "filters")
    extension = ".json"
    model = Filter
    data: FileDeserialize[Filter] = FileDeserialize()


class FilterBase(BaseModel):
    def apply(self, ctx: Context, block_map: BlockMap) -> None:
        raise NotImplementedError()


class GroupFilter(FilterBase):
    """Group multiple filters together."""

    type: Literal["group"]

    children: list[FilterLink]

    def apply(self, ctx: Context, block_map: BlockMap):
        # Apply all child filters, in order.
        for child_link in self.children:
            child = child_link(ctx)
            child.__root__.apply(ctx, block_map)


class KeepFilter(FilterBase):
    """Keep blocks of a certain type."""

    type: Literal["keep"]

    keep: list[BlockProvider]

    def apply(self, ctx: Context, block_map: BlockMap):
        blocks = [block(ctx) for block in self.keep]
        block_map.keep_blocks(blocks)


class RemoveFilter(FilterBase):
    """Remove blocks of a certain type."""

    type: Literal["remove"]

    remove: list[BlockProvider]

    def apply(self, ctx: Context, block_map: BlockMap):
        blocks = [block(ctx) for block in self.remove]
        block_map.remove_blocks(blocks)


class ReplaceFilter(FilterBase):
    """Replace blocks of a certain type with another type."""

    type: Literal["replace"]

    replace: list[BlockProvider]
    replacement: BlockProvider

    def apply(self, ctx: Context, block_map: BlockMap):
        blocks = [block(ctx) for block in self.replace]
        replacement = self.replacement(ctx)
        block_map.replace_blocks(blocks, replacement)


Filter.update_forward_refs()
