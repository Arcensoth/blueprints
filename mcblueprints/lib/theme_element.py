import re
from typing import Any

from beet import Context

from mcblueprints.lib.block import Block
from mcblueprints.lib.normalizable_model import NormalizableModel
from mcblueprints.lib.theme import ThemeLink

__all__ = ["ThemeElement"]


THEME_ELEMENT_PATTERN = re.compile(
    r"^([0-9a-z_\-\.]+\:[0-9a-z_\-\.\/]+)\[([0-9a-z_\-\.]+)\]$"
)


class ThemeElement(NormalizableModel):
    theme: ThemeLink
    element: str

    @classmethod
    def normalize_input(cls, value: Any) -> Any:
        if isinstance(value, str):
            if match := THEME_ELEMENT_PATTERN.match(value):
                theme_name = match.group(1)
                element_name = match.group(2)
                return dict(theme=theme_name, element=element_name)
            raise ValueError(f"Invalid theme element expression: {value}")
        return value

    def __call__(self, ctx: Context) -> Block:
        theme = self.theme(ctx)
        if element := theme.elements.get(self.element):
            return element
        raise KeyError(f"No element {self.element} in theme {self.theme.__root__}")
