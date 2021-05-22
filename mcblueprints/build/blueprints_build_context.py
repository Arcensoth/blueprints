import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from logging import Logger, getLogger
from pathlib import Path
from typing import Any, Optional, Set, Tuple, cast

from pyckaxe import (
    CommonResourceLocationResolver,
    CommonResourceResolver,
    CommonResourceScanner,
    JsonResourceLoader,
    LRUResourceCache,
    NbtResourceDumper,
    PhysicalPack,
    PhysicalRegistryLocation,
    ResourceCache,
    ResourceDumperSet,
    ResourceLocationResolverSet,
    ResourceProcessingContext,
    ResourceResolverSet,
    ResourceScannerSet,
    ResourceTransformerSet,
    StaticResourceCache,
    Structure,
    StructureSerializer,
    UnboundedResourceCache,
    WritablePack,
)
from pyckaxe.utils import walk_exception

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

DEFAULT_BLUEPRINTS_REGISTRY = "blueprints"
DEFAULT_FILTERS_REGISTRY = "filters"
DEFAULT_MATERIALS_REGISTRY = "materials"

DEFAULT_BLUEPRINT_CACHE_SIZE = 1000
DEFAULT_FILTER_CACHE_SIZE = 1000
DEFAULT_MATERIAL_CACHE_SIZE = 1000

DEFAULT_MATCH_FILES = "[!!]*"

DEFAULT_GENERATED_STRUCTURES_REGISTRY = "structures"


@dataclass
class BlueprintsBuildContext:
    input_path: Path
    output_path: Path

    data_version: int

    match_files: str = DEFAULT_MATCH_FILES

    blueprints_registry: str = DEFAULT_BLUEPRINTS_REGISTRY
    filters_registry: str = DEFAULT_FILTERS_REGISTRY
    materials_registry: str = DEFAULT_MATERIALS_REGISTRY

    blueprint_cache_size: int = DEFAULT_BLUEPRINT_CACHE_SIZE
    filter_cache_size: int = DEFAULT_FILTER_CACHE_SIZE
    material_cache_size: int = DEFAULT_MATERIAL_CACHE_SIZE

    generated_structures_registry: str = DEFAULT_GENERATED_STRUCTURES_REGISTRY

    generated_namespace: Optional[str] = None
    generated_prefix: Optional[str] = None

    log: Logger = field(default=DEFAULT)

    blueprint_cache: ResourceCache[Blueprint] = field(default=DEFAULT)
    filter_cache: ResourceCache[Filter] = field(default=DEFAULT)
    material_cache: ResourceCache[Material] = field(default=DEFAULT)

    blueprint_deserializer: BlueprintDeserializer = field(default=DEFAULT)
    filter_deserializer: FilterDeserializer = field(default=DEFAULT)
    material_deserializer: MaterialDeserializer = field(default=DEFAULT)

    material_loader: JsonResourceLoader[Material] = field(default=DEFAULT)
    filter_loader: JsonResourceLoader[Filter] = field(default=DEFAULT)
    blueprint_loader: JsonResourceLoader[Blueprint] = field(default=DEFAULT)

    blueprints_registry_parts: Tuple[str, ...] = field(init=False)
    filters_registry_parts: Tuple[str, ...] = field(init=False)
    materials_registry_parts: Tuple[str, ...] = field(init=False)
    generated_structures_registry_parts: Tuple[str, ...] = field(init=False)

    generated_prefix_parts: Optional[Tuple[str, ...]] = field(init=False)

    transformers: ResourceTransformerSet = field(
        init=False, default_factory=lambda: ResourceTransformerSet()
    )
    blueprint_transformer: BlueprintTransformer = field(default=DEFAULT)

    dumpers: ResourceDumperSet = field(
        init=False, default_factory=lambda: ResourceDumperSet()
    )
    structure_dumper: NbtResourceDumper[Structure] = field(default=DEFAULT)

    input_pack: PhysicalPack = field(init=False)

    build_errors: Set[Exception] = field(init=False, default_factory=set)

    def __str__(self) -> str:
        return self.output_path.name

    def __post_init__(self):
        # Make sure the output path is absolute.
        if not self.output_path.is_absolute():
            raise ValueError(
                f"Expected absolute output path, but got: {self.output_path}"
            )
        # Create a logger, if one does not already exist.
        if self.log is DEFAULT:
            self.log = getLogger(f"{self}")
        # Split paths into parts.
        self.blueprints_registry_parts = tuple(self.blueprints_registry.split("/"))
        self.filters_registry_parts = tuple(self.filters_registry.split("/"))
        self.materials_registry_parts = tuple(self.materials_registry.split("/"))
        self.generated_structures_registry_parts = tuple(
            self.generated_structures_registry.split("/")
        )
        self.generated_prefix_parts = (
            tuple(self.generated_prefix.split("/")) if self.generated_prefix else None
        )
        # Create caches that do not already exist.
        if self.blueprint_cache is DEFAULT:
            if self.blueprint_cache_size > 0:
                self.blueprint_cache = LRUResourceCache(size=self.blueprint_cache_size)
            elif self.blueprint_cache_size == 0:
                self.blueprint_cache = StaticResourceCache()
            else:
                self.blueprint_cache = UnboundedResourceCache()
        if self.filter_cache is DEFAULT:
            if self.filter_cache_size > 0:
                self.filter_cache = LRUResourceCache(size=self.filter_cache_size)
            elif self.filter_cache_size == 0:
                self.filter_cache = StaticResourceCache()
            else:
                self.filter_cache = UnboundedResourceCache()
        if self.material_cache is DEFAULT:
            if self.material_cache_size > 0:
                self.material_cache = LRUResourceCache(size=self.material_cache_size)
            elif self.material_cache_size == 0:
                self.material_cache = StaticResourceCache()
            else:
                self.material_cache = UnboundedResourceCache()
        # Create serializers that do no already exist.
        if self.material_deserializer is DEFAULT:
            self.material_deserializer = MaterialDeserializer()
        if self.filter_deserializer is DEFAULT:
            self.filter_deserializer = FilterDeserializer(
                material_deserializer=self.material_deserializer,
            )
        if self.blueprint_deserializer is DEFAULT:
            self.blueprint_deserializer = BlueprintDeserializer(
                filter_deserializer=self.filter_deserializer,
                material_deserializer=self.material_deserializer,
            )
        # Create loaders that do not already exist.
        if self.blueprint_loader is DEFAULT:
            self.blueprint_loader = JsonResourceLoader(self.blueprint_deserializer)
        if self.filter_loader is DEFAULT:
            self.filter_loader = JsonResourceLoader(self.filter_deserializer)
        if self.material_loader is DEFAULT:
            self.material_loader = JsonResourceLoader(self.material_deserializer)
        # Create and register transformers that do not already exist.
        if self.blueprint_transformer is DEFAULT:
            self.blueprint_transformer = BlueprintTransformer(
                generated_namespace=self.generated_namespace,
                generated_prefix_parts=self.generated_prefix_parts,
            )
        self.transformers[Blueprint] = self.blueprint_transformer
        # Create and register dumpers that do not already exist.
        if self.structure_dumper is DEFAULT:
            self.structure_dumper = NbtResourceDumper(
                serializer=StructureSerializer(data_version=self.data_version),
                options=dict(gzipped=True),
            )
        self.dumpers[Structure] = self.structure_dumper
        # Create a representation of the input pack.
        self.input_pack = PhysicalPack(self.input_path)

    async def build(self):
        self.log.info(f"Reading from: {self.input_path}")
        self.log.info(f"Writing to: {self.output_path}")

        # Collect blueprint registries.
        self.log.info(f"Collecting blueprint registries:")
        blueprint_registries = await self.input_pack.get_registries(
            *self.blueprints_registry_parts
        )
        for registry in blueprint_registries:
            self.log.info(f"  - {registry}")

        # Warn if no registries were found.
        if not blueprint_registries:
            self.log.error(
                f"No blueprint registries found matching: {self.blueprints_registry}"
            )
            return

        # Create a separate task for each registry.
        tasks = [self.build_registry(registry) for registry in blueprint_registries]

        # Start the build timer.
        time_start = datetime.utcnow()

        # Build registries asynchronously from one another.
        await asyncio.gather(*tasks)

        # Stop the build timer.
        time_elapsed = datetime.utcnow() - time_start

        # Let the user know that processing is finished and whether it was successful.
        if self.build_errors:
            self.log.error(
                f"Failed to finish building pack {self}"
                + f" with {len(self.build_errors)} errors:"
            )
            for i, error in enumerate(self.build_errors):
                prefix = f"  [{i + 1}] "
                pad = len(prefix) * " "
                self.log.error(f"{prefix}{error}")
                causes = list(walk_exception(error))
                for cause in causes[:-1]:
                    self.log.error(f"{pad}├ {cause}")
                self.log.error(f"{pad}└ {causes[-1]}")
        else:
            self.log.info(f"Finished building pack {self}")

        # Output some final metrics.
        self.log.info(
            "Number of blueprints cached: "
            + f"{len(self.blueprint_cache)}"
            + (
                f" / {self.blueprint_cache_size}"
                if self.blueprint_cache_size >= 0
                else ""
            )
        )
        self.log.info(
            "Number of blueprint filters cached: "
            + f"{len(self.filter_cache)}"
            + (f" / {self.filter_cache_size}" if self.filter_cache_size >= 0 else "")
        )
        self.log.info(
            "Number of materials cached: "
            + f"{len(self.material_cache)}"
            + (
                f" / {self.material_cache_size}"
                if self.material_cache_size >= 0
                else ""
            )
        )
        self.log.info(f"Time elapsed: {time_elapsed}")

    async def build_registry(self, blueprints_registry: PhysicalRegistryLocation):
        self.log.info(f"Processing registry {blueprints_registry}")
        # Create and register input scanners.
        scanners = ResourceScannerSet(
            CommonResourceScanner[Blueprint](blueprints_registry, Blueprint),
        )
        # Create input location resolvers.
        blueprint_location_resolver = CommonResourceLocationResolver(
            path=blueprints_registry.namespace.path.parent,
            parts=self.blueprints_registry_parts,
        )
        filter_location_resolver = CommonResourceLocationResolver(
            path=blueprints_registry.namespace.path.parent,
            parts=self.filters_registry_parts,
        )
        material_location_resolver = CommonResourceLocationResolver(
            path=blueprints_registry.namespace.path.parent,
            parts=self.materials_registry_parts,
        )
        # Create and register input resolvers.
        resolvers = ResourceResolverSet()
        resolvers[Blueprint] = CommonResourceResolver[Blueprint](
            location_resolver=blueprint_location_resolver,
            loader=self.blueprint_loader,
            cache=self.blueprint_cache,
        )
        resolvers[Filter] = CommonResourceResolver[Filter](
            location_resolver=filter_location_resolver,
            loader=self.filter_loader,
            cache=self.filter_cache,
        )
        resolvers[Material] = CommonResourceResolver[Material](
            location_resolver=material_location_resolver,
            loader=self.material_loader,
            cache=self.material_cache,
        )
        # Create and register output location resolvers.
        output_location_resolvers = ResourceLocationResolverSet()
        output_location_resolvers[Structure] = CommonResourceLocationResolver(
            path=Path(self.output_path / "data"),
            parts=self.generated_structures_registry_parts,
        )
        # Create a representation of the output pack.
        output_pack = WritablePack(
            path=self.output_path,
            location_resolvers=output_location_resolvers,
            dumpers=self.dumpers,
        )
        # Process and transform each type of resource.
        await self.process_all(scanners, resolvers, self.transformers, output_pack)
        # Print a message when we're all done with this registry.
        self.log.info(f"Finished processing registry {blueprints_registry}")

    async def process_all(
        self,
        scanners: ResourceScannerSet,
        resolvers: ResourceResolverSet,
        transformers: ResourceTransformerSet,
        output_pack: WritablePack,
    ):
        for scanner in scanners:
            self.log.info(f"Processing {scanner}")
            count_inputs = 0
            count_outputs = 0
            count_errors = 0
            async for input_location in scanner(match=self.match_files):
                self.log.debug(f"-> {input_location}")
                count_inputs += 1
                try:
                    input_resource = await resolvers(input_location)
                    ctx = ResourceProcessingContext[Any](
                        resolver_set=resolvers,
                        resource=input_resource,
                        location=input_location,
                    )
                    async for output_resource, output_location in transformers(ctx):
                        self.log.debug(
                            f"  -> {output_location} (#{id(output_resource)})"
                        )
                        await output_pack.dump(output_resource, output_location)
                        count_outputs += 1
                except Exception as ex:
                    self.log.exception(
                        f"Error while processing resource {input_location}"
                    )
                    self.build_errors.add(ex)
                    count_errors += 1
            self.log.info(
                f"Finished processing {scanner}"
                + (
                    f" with {count_inputs} inputs -> {count_outputs} outputs"
                    if count_inputs > 0
                    else " (nothing to process)"
                )
                + (f" (with {count_errors} errors)" if count_errors > 0 else "")
            )
