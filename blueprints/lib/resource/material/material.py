from dataclasses import dataclass
from typing import Optional

from pyckaxe import Block, BlockState, NbtCompound, Resource

__all__ = ("Material",)


@dataclass
class Material(Resource):
    block: Block

    def __str__(self) -> str:
        return str(self.block)

    def __repr__(self) -> str:
        return str(self)

    @property
    def name(self) -> str:
        return self.block.name

    @property
    def state(self) -> Optional[BlockState]:
        return self.block.state

    @property
    def data(self) -> Optional[NbtCompound]:
        return self.block.data
