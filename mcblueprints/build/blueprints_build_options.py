from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple

__all__ = ("BlueprintsBuildOptions",)


DEFAULT_BLUEPRINTS_REGISTRY = "blueprints"
DEFAULT_FILTERS_REGISTRY = "filters"
DEFAULT_MATERIALS_REGISTRY = "materials"

DEFAULT_BLUEPRINT_CACHE_SIZE = 1000
DEFAULT_FILTER_CACHE_SIZE = 1000
DEFAULT_MATERIAL_CACHE_SIZE = 1000

DEFAULT_MATCH_FILES = "[!!]*"

DEFAULT_GENERATED_STRUCTURES_REGISTRY = "structures"


@dataclass
class BlueprintsBuildOptions:
    input_path: Path
    output_path: Path

    data_version: int

    match_files: str = DEFAULT_MATCH_FILES

    generated_namespace: Optional[str] = None
    generated_prefix: Optional[str] = None

    blueprints_registry: str = DEFAULT_BLUEPRINTS_REGISTRY
    filters_registry: str = DEFAULT_FILTERS_REGISTRY
    materials_registry: str = DEFAULT_MATERIALS_REGISTRY

    blueprint_cache_size: int = DEFAULT_BLUEPRINT_CACHE_SIZE
    filter_cache_size: int = DEFAULT_FILTER_CACHE_SIZE
    material_cache_size: int = DEFAULT_MATERIAL_CACHE_SIZE

    generated_structures_registry: str = DEFAULT_GENERATED_STRUCTURES_REGISTRY

    generated_prefix_parts: Optional[Tuple[str, ...]] = field(init=False)

    def __post_init__(self):
        # Make sure the output path is absolute.
        if not self.output_path.is_absolute():
            raise ValueError(
                f"Expected absolute output path, but got: {self.output_path}"
            )

        # Split output prefix path into parts.
        self.generated_prefix_parts = (
            tuple(self.generated_prefix.split("/")) if self.generated_prefix else None
        )

        # Split input registry paths into parts.
        self.blueprints_registry_parts = tuple(self.blueprints_registry.split("/"))
        self.filters_registry_parts = tuple(self.filters_registry.split("/"))
        self.materials_registry_parts = tuple(self.materials_registry.split("/"))

        # Split output registry paths into parts.
        self.generated_structures_registry_parts = tuple(
            self.generated_structures_registry.split("/")
        )
