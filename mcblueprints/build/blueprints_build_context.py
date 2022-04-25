from dataclasses import dataclass, field
from logging import Logger, getLogger
from pathlib import Path
from typing import Any, cast

from pyckaxe import (
    CommonResourceResolver,
    JsonResourceLoader,
    LRUResourceCache,
    MatchingResourceLocationResolver,
    NbtResourceDumper,
    ResourceCache,
    ResourceCacheSet,
    ResourceDumperSet,
    ResourceLocationResolverSet,
    ResourceProcessingPipeline,
    ResourceResolverSet,
    ResourceTransformerSet,
    StaticResourceCache,
    StaticResourceLocationResolver,
    Structure,
    StructureSerializer,
    UnboundedResourceCache,
)
from pyckaxe.lib.pack.common_resource_scanner import CommonResourceScanner
from pyckaxe.lib.pack.physical_pack import PhysicalPack
from pyckaxe.lib.pack.writable_pack import WritablePack

from mcblueprints.build.blueprints_build_options import BlueprintsBuildOptions
from mcblueprints.lib import (
    Blueprint,
    BlueprintDeserializer,
    BlueprintTransformer,
    Filter,
    FilterDeserializer,
    Material,
    MaterialDeserializer,
)

__all__ = ("BlueprintsBuildContext",)


DEFAULT = cast(Any, ...)


@dataclass
class BlueprintsBuildContext:
    options: BlueprintsBuildOptions

    log: Logger = field(init=False, default=DEFAULT)

    pipeline: ResourceProcessingPipeline = field(init=False, default=DEFAULT)

    def __str__(self) -> str:
        return self.options.output_path.name

    def __post_init__(self):
        # Create a logger.
        self.log = getLogger(f"{self}")

        # Create and register caches.
        caches = ResourceCacheSet()
        caches[Blueprint] = self._make_cache(self.options.blueprint_cache_size)
        caches[Filter] = self._make_cache(self.options.filter_cache_size)
        caches[Material] = self._make_cache(self.options.material_cache_size)

        # Create serializers.
        material_deserializer = MaterialDeserializer()
        filter_deserializer = FilterDeserializer()
        blueprint_deserializer = lambda data, **kwargs: Blueprint.parse_obj(data)

        # Create and register input resolvers.
        resolvers = ResourceResolverSet()
        resolvers[Blueprint] = CommonResourceResolver[Blueprint](
            location_resolver=MatchingResourceLocationResolver(
                root=Path(self.options.input_path / "data"),
                registry_parts=self.options.blueprints_registry_parts,
            ),
            loader=JsonResourceLoader(blueprint_deserializer),
            cache=caches[Blueprint],
        )
        resolvers[Filter] = CommonResourceResolver[Filter](
            location_resolver=MatchingResourceLocationResolver(
                root=Path(self.options.input_path / "data"),
                registry_parts=self.options.filters_registry_parts,
            ),
            loader=JsonResourceLoader(filter_deserializer),
            cache=caches[Filter],
        )
        resolvers[Material] = CommonResourceResolver[Material](
            location_resolver=MatchingResourceLocationResolver(
                root=Path(self.options.input_path / "data"),
                registry_parts=self.options.materials_registry_parts,
            ),
            loader=JsonResourceLoader(material_deserializer),
            cache=caches[Material],
        )

        # Create and register transformers.
        transformers = ResourceTransformerSet()
        transformers[Blueprint] = BlueprintTransformer(
            generated_namespace=self.options.generated_namespace,
            generated_prefix_parts=self.options.generated_prefix_parts,
        )

        # Create and register output location resolvers.
        output_location_resolvers = ResourceLocationResolverSet()
        output_location_resolvers[Structure] = StaticResourceLocationResolver(
            root=Path(self.options.output_path / "data"),
            registry_parts=self.options.generated_structures_registry_parts,
            suffix=".nbt",
        )

        # Create and register output dumpers.
        output_dumpers = ResourceDumperSet()
        output_dumpers[Structure] = NbtResourceDumper(
            serializer=StructureSerializer(data_version=self.options.data_version),
            options=dict(gzipped=True),
        )

        # Create a representation of the input pack.
        input_pack = PhysicalPack(self.options.input_path)

        # Create a representation of the output pack.
        output_pack = WritablePack(
            path=self.options.output_path,
            location_resolvers=output_location_resolvers,
            dumpers=output_dumpers,
        )

        # Create a pipeline to encapsulate everything.
        self.pipeline = ResourceProcessingPipeline(
            input_pack=input_pack,
            output_pack=output_pack,
            scanner_factory=CommonResourceScanner,
            caches=caches,
            resolvers=resolvers,
            transformers=transformers,
            match_files=self.options.match_files,
        )

    def _make_cache(self, cache_size: int) -> ResourceCache[Any]:
        if cache_size > 0:
            return LRUResourceCache(size=cache_size)
        elif cache_size == 0:
            return StaticResourceCache()
        return UnboundedResourceCache()

    async def build(self):
        await self.pipeline.process(
            {
                Blueprint: self.options.blueprints_registry_parts,
            }
        )
