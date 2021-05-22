from typing import Union

from pyckaxe import ClassifiedResourceLocation, ResourceProcessingContext

from mcblueprints.lib.resource.material.material import Material

MaterialLocation = ClassifiedResourceLocation[Material]
MaterialOrLocation = Union[Material, MaterialLocation]
MaterialProcessingContext = ResourceProcessingContext[Material]
