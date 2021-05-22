from pathlib import Path
from typing import Any

import click
from pyckaxe.cli.utils import asyncify
from pyckaxe.utils import LOG_LEVELS, setup_logging

from mcblueprints import __version__
from mcblueprints.build.blueprints_build_context import (
    DEFAULT_BLUEPRINT_CACHE_SIZE,
    DEFAULT_BLUEPRINTS_REGISTRY,
    DEFAULT_FILTER_CACHE_SIZE,
    DEFAULT_FILTERS_REGISTRY,
    DEFAULT_GENERATED_STRUCTURES_REGISTRY,
    DEFAULT_MATCH_FILES,
    DEFAULT_MATERIAL_CACHE_SIZE,
    DEFAULT_MATERIALS_REGISTRY,
    BlueprintsBuildContext,
)

__all__ = ("run",)


PROG_NAME = "mcblueprints"


@click.group()
@click.version_option(__version__, "-v", "--version")
@click.option(
    "-l",
    "--log",
    type=click.Choice(LOG_LEVELS, case_sensitive=False),
    default=LOG_LEVELS[2],
    help="The level of verbosity to log at.",
)
@click.option(
    "-ll",
    "--detailed-logs/--no-detailed-logs",
    default=False,
    help="Whether to use the detailed logging format.",
)
def cli(log: str, detailed_logs: bool):
    setup_logging(level=log.upper(), detailed=detailed_logs)


@cli.command(
    "build",
    help="Build Minecraft structures from mcblueprints.",
)
@click.option(
    "--input",
    "input_path",
    type=click.Path(exists=True, resolve_path=True),
    required=True,
    callback=lambda ctx, param, value: Path(value),
    help="The path to the data pack to read the input.",
)
@click.option(
    "--output",
    "output_path",
    type=click.Path(resolve_path=True),
    required=True,
    callback=lambda ctx, param, value: Path(value),
    help="The path to the data pack to dump the output.",
)
@click.option(
    "--data_version",
    "data_version",
    type=int,
    required=True,
    help="The data version to use in generated structures.",
)
@click.option(
    "--match_files",
    "match_files",
    type=str,
    help="The glob pattern to match files against."
    + f" Defaults to: {DEFAULT_MATCH_FILES}",
)
@click.option(
    "--blueprints_registry",
    "blueprints_registry",
    type=str,
    help="The registry where custom blueprints are located."
    + f" Defaults to: {DEFAULT_BLUEPRINTS_REGISTRY}",
)
@click.option(
    "--filters_registry",
    "filters_registry",
    type=str,
    help="The registry where custom filters are located."
    + f" Defaults to: {DEFAULT_FILTERS_REGISTRY}",
)
@click.option(
    "--materials_registry",
    "materials_registry",
    type=str,
    help="The registry where custom materials are located."
    + f" Defaults to: {DEFAULT_MATERIALS_REGISTRY}",
)
@click.option(
    "--blueprint_cache_size",
    type=int,
    help="The maximum number of blueprints to keep cached in memory."
    + "Set to 0 to disable caching. Set to -1 for an unbounded cache."
    + f" Defaults to: {DEFAULT_BLUEPRINT_CACHE_SIZE}",
)
@click.option(
    "--filter_cache_size",
    type=int,
    help="The maximum number of filters to keep cached in memory."
    + "Set to 0 to disable caching. Set to -1 for an unbounded cache."
    + f" Defaults to: {DEFAULT_FILTER_CACHE_SIZE}",
)
@click.option(
    "--material_cache_size",
    type=int,
    help="The maximum number of materials to keep cached in memory."
    + "Set to 0 to disable caching. Set to -1 for an unbounded cache."
    + f" Defaults to: {DEFAULT_MATERIAL_CACHE_SIZE}",
)
@click.option(
    "--generated_structures_registry",
    "generated_structures_registry",
    type=str,
    help="The registry where vanilla structures are located."
    + f" Defaults to: {DEFAULT_GENERATED_STRUCTURES_REGISTRY}",
)
@click.option(
    "--generated_namespace",
    "generated_namespace",
    type=str,
    help="A separate namespace to use for generated resources.",
)
@click.option(
    "--generated_prefix",
    "generated_prefix",
    type=str,
    help="A prefix to apply to the locations of generated resources.",
)
@asyncify
async def cli_build(**kwargs: Any):
    filtered_args = {k: v for k, v in kwargs.items() if v is not None}
    ctx = BlueprintsBuildContext(**filtered_args)
    await ctx.build()


def run():
    cli(prog_name=PROG_NAME)
