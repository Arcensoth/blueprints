from typing import Annotated, Any, Literal, Union

from beet import Context
from pydantic import BaseModel, Field

from mcblueprints.lib.block import Block
from mcblueprints.lib.normalizable_model import NormalizableModel
from mcblueprints.lib.template_variable import TemplateVariable
from mcblueprints.lib.theme_element import ThemeElement

__all__ = ["BlockProvider"]


class BlockProvider(NormalizableModel):
    __root__: Annotated[
        Union[
            "BlockBlockProvider",
            "VariableBlockProvider",
            "ThemedBlockProvider",
        ],
        Field(discriminator="type"),
    ]

    @classmethod
    def normalize_input(cls, value: Any) -> Any:
        if isinstance(value, str):
            if value.startswith("@"):
                return dict(type="themed", element=value[1:])
            if value.startswith("$"):
                return dict(type="variable", variable=value[1:])
            return dict(type="block", block=value)
        return value

    def __call__(self, ctx: Context) -> Block:
        return self.__root__(ctx)


class BlockProviderBase(BaseModel):
    def __call__(self, ctx: Context) -> Block:
        raise NotImplementedError()


class BlockBlockProvider(BlockProviderBase):
    type: Literal["block"]

    block: Block

    def __call__(self, ctx: Context) -> Block:
        return self.block


class VariableBlockProvider(BlockProviderBase):
    type: Literal["variable"]

    variable: TemplateVariable

    def __call__(self, ctx: Context) -> Block:
        return self.variable.to_block()


class ThemedBlockProvider(BlockProviderBase):
    type: Literal["themed"]

    element: ThemeElement

    def __call__(self, ctx: Context) -> Block:
        return self.element(ctx)


BlockProvider.update_forward_refs()
