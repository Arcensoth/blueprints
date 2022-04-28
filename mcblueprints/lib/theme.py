from beet import Context, FileDeserialize, JsonFileBase
from pydantic import BaseModel

from mcblueprints.lib.block import Block
from mcblueprints.lib.normalizable_model import NormalizableModel

__all__ = ["Theme", "ThemeLink", "ThemeFile"]


class Theme(NormalizableModel):
    elements: dict[str, Block]


class ThemeLink(BaseModel):
    __root__: str | Theme

    def __call__(self, ctx: Context) -> Theme:
        if isinstance((self.__root__), str):
            if theme := ctx.data[ThemeFile].get(self.__root__):
                return theme.data
            raise KeyError(f"No such theme {self.__root__}")
        return self.__root__


class ThemeFile(JsonFileBase[Theme]):
    scope = ("blueprints", "themes")
    extension = ".json"
    model = Theme
    data: FileDeserialize[Theme] = FileDeserialize()
