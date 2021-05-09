from dataclasses import dataclass
from typing import Optional

from pyckaxe.lib import (
    Block,
    BlockState,
    JsonValue,
    NbtCompound,
    ResourceLocation,
    to_nbt_compound,
)

from blueprints.lib.resource.material.material import Material
from blueprints.lib.resource.material.types import MaterialOrLocation

__all__ = ("MaterialDeserializer",)


class MaterialDeserializationException(Exception):
    pass


class MalformedMaterial(MaterialDeserializationException):
    def __init__(self, raw: JsonValue):
        self.raw: JsonValue = raw
        super().__init__(raw, f"Malformed material")


class MissingBlock(MaterialDeserializationException):
    def __init__(self, raw: JsonValue):
        self.raw: JsonValue = raw
        super().__init__(f"Missing block")


class InvalidBlock(MaterialDeserializationException):
    def __init__(self, block: JsonValue):
        self.block: JsonValue = block
        super().__init__(f"Invalid block: {block}")


class InvalidState(MaterialDeserializationException):
    def __init__(self, state: JsonValue):
        self.state: JsonValue = state
        super().__init__(f"Invalid state: {state}")


class InvalidData(MaterialDeserializationException):
    def __init__(self, data: JsonValue):
        self.data: JsonValue = data
        super().__init__(f"Invalid data: {data}")


# @implements ResourceDeserializer[JsonValue, Material]
@dataclass
class MaterialDeserializer:
    # @implements ResourceDeserializer
    def __call__(self, raw: JsonValue) -> Material:
        return self.deserialize(raw)

    def or_location(self, raw: JsonValue) -> MaterialOrLocation:
        """ Deserialize a material or location from a raw value. """
        # A string is assumed to be a resource location.
        if isinstance(raw, str):
            return Material @ ResourceLocation.from_string(raw)
        # Anything else is assumed to be a serialized resource.
        return self(raw)

    def deserialize(self, raw: JsonValue) -> Material:
        """ Deserialize a `Material` from a raw value. """
        try:
            if not isinstance(raw, dict):
                raise MalformedMaterial(raw)

            name = raw.get("block")
            if not name:
                raise MissingBlock(raw)
            if not isinstance(name, str):
                raise InvalidBlock(name)

            state: Optional[BlockState] = None
            if raw_state := raw.get("state"):
                try:
                    assert isinstance(raw_state, dict)
                    state = BlockState(**raw_state)
                except Exception as ex:
                    raise InvalidState(raw_state) from ex

            data: Optional[NbtCompound] = None
            if raw_data := raw.get("data"):
                try:
                    assert isinstance(raw_data, dict)
                    data = to_nbt_compound(raw_data)
                except Exception as ex:
                    raise InvalidData(raw_data) from ex

            block = Block(
                name=name,
                state=state,
                data=data,
            )

            return Material(block)

        except MaterialDeserializationException as ex:
            raise ex

        except Exception as ex:
            raise MalformedMaterial(raw) from ex
