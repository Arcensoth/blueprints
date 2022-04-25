import json
from dataclasses import dataclass
from typing import Any

from beet import Context, FileDeserialize, JsonFileBase
from pydantic import BaseModel

from mcblueprints.lib import Blueprint, Filter, Material


def beet_default(ctx: Context):
    ctx.inject(MaterialManager)
    ctx.inject(FilterManager)
    ctx.inject(BlueprintManager)

    yield

    print()
    print("Materials:")
    print()
    for name, item in ctx.data[MaterialFile].items():
        print()
        print(f"  {name}")
        print(f"    {repr(item.data)}")

    print()
    print("Filters:")
    print()
    for name, item in ctx.data[FilterFile].items():
        print()
        print(f"  {name}")
        print(f"    {repr(item.data)}")

    print()
    print("Blueprints:")
    print()
    for name, item in ctx.data[BlueprintFile].items():
        print()
        print(f"  {name}")
        print(f"    {repr(item.data)}")

    print()


class FileCommon:
    model: Any

    @classmethod
    def from_str(cls, content: str):
        value = json.loads(content)
        if cls.model and issubclass(cls.model, BaseModel):
            value = cls.model.parse_obj(value)
        return value  # type: ignore


class MaterialFile(JsonFileBase[Material], FileCommon):
    """Class representing a material file."""

    scope = ("materials",)
    extension = ".json"
    model = Material

    data: FileDeserialize[Material] = FileDeserialize()


class FilterFile(JsonFileBase[Filter], FileCommon):
    """Class representing a filter file."""

    scope = ("filters",)
    extension = ".json"
    model = Filter

    data: FileDeserialize[Filter] = FileDeserialize()


class BlueprintFile(JsonFileBase[Blueprint], FileCommon):
    """Class representing a blueprint file."""

    scope = ("blueprints",)
    extension = ".json"
    model = Blueprint

    data: FileDeserialize[Blueprint] = FileDeserialize()


@dataclass
class MaterialManager:
    """Service for managing materials."""

    ctx: Context

    def __post_init__(self):
        self.ctx.require(self.cleanup)
        self.ctx.data.extend_namespace.append(MaterialFile)

    def cleanup(self, ctx: Context):
        """Plugin that removes all materials at the end of the build."""
        yield
        ctx.data[MaterialFile].clear()


@dataclass
class FilterManager:
    """Service for managing filters."""

    ctx: Context

    def __post_init__(self):
        self.ctx.require(self.cleanup)
        self.ctx.data.extend_namespace.append(FilterFile)

    def cleanup(self, ctx: Context):
        """Plugin that removes all filters at the end of the build."""
        yield
        ctx.data[FilterFile].clear()


@dataclass
class BlueprintManager:
    """Service for managing blueprints."""

    ctx: Context

    def __post_init__(self):
        self.ctx.require(self.cleanup)
        self.ctx.data.extend_namespace.append(BlueprintFile)

    def cleanup(self, ctx: Context):
        """Plugin that removes all blueprints at the end of the build."""
        yield
        ctx.data[BlueprintFile].clear()
