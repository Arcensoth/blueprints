from typing import Union

from pyckaxe.lib import ClassifiedResourceLocation, ResourceProcessingContext

from blueprints.lib.resource.blueprint.blueprint import Blueprint

BlueprintLocation = ClassifiedResourceLocation[Blueprint]
BlueprintOrLocation = Union[Blueprint, BlueprintLocation]
BlueprintProcessingContext = ResourceProcessingContext[Blueprint]
