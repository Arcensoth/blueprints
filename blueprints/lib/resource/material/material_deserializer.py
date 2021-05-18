from dataclasses import dataclass
from typing import Optional

from pyckaxe import (
    Block,
    BlockState,
    Breadcrumb,
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
    def __init__(self, message: str, raw_material: JsonValue, breadcrumb: Breadcrumb):
        self.raw_material: JsonValue = raw_material
        self.breadcrumb: Breadcrumb = breadcrumb
        super().__init__(message)


# @implements ResourceDeserializer[JsonValue, Material]
@dataclass
class MaterialDeserializer:
    # @implements ResourceDeserializer
    def __call__(
        self,
        raw: JsonValue,
        *,
        breadcrumb: Optional[Breadcrumb] = None,
    ) -> Material:
        return self.deserialize(raw, breadcrumb or Breadcrumb())

    def or_location(self, raw: JsonValue, breadcrumb: Breadcrumb) -> MaterialOrLocation:
        """ Deserialize a `Material` or `MaterialLocation` from a raw value. """
        # A string is assumed to be a resource location.
        if isinstance(raw, str):
            return Material @ ResourceLocation.from_string(raw)
        # Anything else is assumed to be a serialized resource.
        return self(raw, breadcrumb=breadcrumb)

    def deserialize(self, raw_material: JsonValue, breadcrumb: Breadcrumb) -> Material:
        """ Deserialize a `Material` from a raw value. """
        if not isinstance(raw_material, dict):
            raise MalformedMaterial(
                f"Malformed material, at `{breadcrumb}`", raw_material, breadcrumb
            )

        # name (required, non-nullable, no default)
        raw_name = raw_material.get("block")
        breadcrumb_name = breadcrumb.name
        if not raw_name:
            raise MalformedMaterial(
                f"Missing `name`, at `{breadcrumb_name}`", raw_material, breadcrumb_name
            )
        name = self.deserialize_name(raw_name, breadcrumb_name)

        # state (optional, nullable, defaults to null)
        state: Optional[BlockState] = None
        if (raw_state := raw_material.get("state")) is not None:
            state = self.deserialize_state(raw_state, breadcrumb.state)

        # data (optional, nullable, defaults to null)
        data: Optional[NbtCompound] = None
        if (raw_data := raw_material.get("data")) is not None:
            data = self.deserialize_data(raw_data, breadcrumb.data)

        block = Block(
            name=name,
            state=state,
            data=data,
        )

        material = Material(block)

        return material

    def deserialize_name(self, raw_name: JsonValue, breadcrumb: Breadcrumb) -> str:
        if not isinstance(raw_name, str):
            raise MalformedMaterial(
                f"Malformed `name`, at `{breadcrumb}`", raw_name, breadcrumb
            )
        return raw_name

    def deserialize_state(
        self, raw_state: JsonValue, breadcrumb: Breadcrumb
    ) -> BlockState:
        try:
            assert isinstance(raw_state, dict)
            return BlockState(**raw_state)
        except Exception as ex:
            raise MalformedMaterial(
                f"Malformed `state`, at `{breadcrumb}`", raw_state, breadcrumb
            ) from ex

    def deserialize_data(
        self, raw_data: JsonValue, breadcrumb: Breadcrumb
    ) -> NbtCompound:
        try:
            assert isinstance(raw_data, dict)
            return to_nbt_compound(raw_data)
        except Exception as ex:
            raise MalformedMaterial(
                f"Malformed `data`, at `{breadcrumb}`", raw_data, breadcrumb
            ) from ex
