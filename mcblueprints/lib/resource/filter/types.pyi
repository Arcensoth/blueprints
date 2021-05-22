from typing import Union

from pyckaxe import ClassifiedResourceLocation, ResourceProcessingContext

from mcblueprints.lib.resource.filter.filter import Filter

FilterLocation = ClassifiedResourceLocation[Filter]
FilterOrLocation = Union[Filter, FilterLocation]
FilterProcessingContext = ResourceProcessingContext[Filter]
