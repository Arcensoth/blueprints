import re
from typing import Any

from mcblueprints.lib.block import Block
from mcblueprints.lib.normalizable_model import NormalizableModel

__all__ = ["TemplateVariable"]


TEMPLATE_VARIABLE_PATTERN = re.compile(r"^([0-9a-z_\-\.]+)$")

VARIABLE_BLOCK = Block(name="blueprints:variable")


class TemplateVariable(NormalizableModel):
    name: str

    @classmethod
    def normalize_input(cls, value: Any) -> Any:
        if isinstance(value, str):
            if match := TEMPLATE_VARIABLE_PATTERN.match(value):
                variable_name = match.group(1)
                return dict(name=variable_name)
            raise ValueError(f"Invalid template variable expression: {value}")
        return value

    def to_block(self) -> Block:
        return VARIABLE_BLOCK.with_state(name=self.name)
