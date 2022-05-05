import logging
from dataclasses import dataclass

from beet import Context, Structure, configurable
from pydantic import BaseModel

from mcblueprints.lib import FilterFile, TemplateFile, ThemeFile
from mcblueprints.lib.structure_serializer import StructureSerializer

LOG = logging.getLogger("blueprints")

__all__ = ["beet_default"]


class BlueprintsOptions(BaseModel):
    data_version: int = 3095  # 22w18a
    output_location: str = "{namespace}:{path}"


def beet_default(ctx: Context):
    ctx.require(blueprints)


@configurable(validator=BlueprintsOptions)
def blueprints(ctx: Context, opts: BlueprintsOptions):
    ctx.inject(ThemeManager)
    ctx.inject(FilterManager)
    ctx.inject(TemplateManager)

    yield

    structure_serializer = StructureSerializer(data_version=opts.data_version)
    items = list(ctx.data[TemplateFile].items())
    for name, item in items:
        LOG.info(f"Building template: {name}")
        try:
            structure_data = item.data.to_structure_data(ctx)
            structure_nbt = structure_serializer(structure_data)
            structure = Structure(structure_nbt)
            namespace, _, path = name.partition(":")
            location = opts.output_location.format(namespace=namespace, path=path)
            ctx.data[location] = structure
        except:
            LOG.exception(f"Error while building template: {name}")


@dataclass
class ThemeManager:
    """Service for managing themes."""

    ctx: Context

    def __post_init__(self):
        self.ctx.require(self.cleanup)
        self.ctx.data.extend_namespace.append(ThemeFile)

    def cleanup(self, ctx: Context):
        """Plugin that removes all themes at the end of the build."""
        yield
        ctx.data[ThemeFile].clear()


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
class TemplateManager:
    """Service for managing templates."""

    ctx: Context

    def __post_init__(self):
        self.ctx.require(self.cleanup)
        self.ctx.data.extend_namespace.append(TemplateFile)

    def cleanup(self, ctx: Context):
        """Plugin that removes all templates at the end of the build."""
        yield
        ctx.data[TemplateFile].clear()
