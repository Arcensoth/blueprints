from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from pyckaxe import Breadcrumb, JsonValue, ResourceLocation

from blueprints.lib.resource.filter.filter import Filter, FilterRule
from blueprints.lib.resource.filter.rule.keep_materials_filter_rule import (
    KeepMaterialsFilterRule,
)
from blueprints.lib.resource.filter.rule.replace_materials_filter_rule import (
    ReplaceMaterialsFilterRule,
)
from blueprints.lib.resource.filter.types import FilterOrLocation
from blueprints.lib.resource.material.material_deserializer import MaterialDeserializer

__all__ = ("FilterDeserializer",)


class FilterDeserializationException(Exception):
    pass


class MalformedFilter(FilterDeserializationException):
    def __init__(self, message: str, raw_filter: JsonValue, breadcrumb: Breadcrumb):
        self.raw_filter: JsonValue = raw_filter
        self.breadcrumb: Breadcrumb = breadcrumb
        super().__init__(message)


class MalformedRule(FilterDeserializationException):
    def __init__(self, message: str, raw_rule: JsonValue, breadcrumb: Breadcrumb):
        self.raw_rule = raw_rule
        self.breadcrumb: Breadcrumb = breadcrumb
        super().__init__(message)


# @implements ResourceDeserializer[JsonValue, Filter]
@dataclass
class FilterDeserializer:
    material_deserializer: MaterialDeserializer

    # @implements ResourceDeserializer
    def __call__(
        self,
        raw: JsonValue,
        *,
        breadcrumb: Optional[Breadcrumb] = None,
    ) -> Filter:
        return self.deserialize(raw, breadcrumb or Breadcrumb())

    def or_location(self, raw: JsonValue, breadcrumb: Breadcrumb) -> FilterOrLocation:
        """ Deserialize a `Filter` or `FilterLocation` from a raw value. """
        # A string is assumed to be a resource location.
        if isinstance(raw, str):
            return Filter @ ResourceLocation.from_string(raw)
        # Anything else is assumed to be a serialized resource.
        return self(raw, breadcrumb=breadcrumb)

    def deserialize(self, raw_filter: JsonValue, breadcrumb: Breadcrumb) -> Filter:
        """ Deserialize a `Filter` from a raw value. """
        if isinstance(raw_filter, dict):
            # rules (required, non-nullable, no default)
            raw_rules = raw_filter.get("rules")
            breadcrumb_rules = breadcrumb.rules
            if raw_rules is None:
                raise MalformedFilter(
                    f"Missing `rules`, at `{breadcrumb_rules}`",
                    raw_filter,
                    breadcrumb_rules,
                )
            rules = self.deserialize_rules(raw_rules, breadcrumb_rules)

        elif isinstance(raw_filter, list):
            rules = self.deserialize_rules(raw_filter, breadcrumb)

        else:
            raise MalformedFilter(
                f"Malformed filter, at `{breadcrumb}`", raw_filter, breadcrumb
            )

        filter = Filter(rules=rules)

        return filter

    def deserialize_rules(
        self, raw_rules: JsonValue, breadcrumb: Breadcrumb
    ) -> List[FilterRule]:
        if not isinstance(raw_rules, list):
            raise MalformedFilter(
                f"Malformed `rules`, at `{breadcrumb}`", raw_rules, breadcrumb
            )
        rules = [
            self.deserialize_rule(raw_rule, breadcrumb[i])
            for i, raw_rule in enumerate(raw_rules)
        ]
        return rules

    def deserialize_rule(
        self, raw_rule: JsonValue, breadcrumb: Breadcrumb
    ) -> FilterRule:
        if not isinstance(raw_rule, dict):
            raise MalformedRule(
                f"Malformed rule, at `{breadcrumb}`", raw_rule, breadcrumb
            )

        rule_type = raw_rule.get("type")
        breadcrumb_type = breadcrumb.type
        if rule_type is None:
            raise MalformedRule(
                f"Missing `type`, at `{breadcrumb_type}`", raw_rule, breadcrumb_type
            )
        if not isinstance(rule_type, str):
            raise MalformedRule(
                f"Malformed `type`, at `{breadcrumb_type}`", raw_rule, breadcrumb_type
            )

        rule_deserializers: Dict[
            str, Callable[[Dict[str, JsonValue], Breadcrumb], FilterRule]
        ] = {
            "keep_materials": self.deserialize_keep_materials_rule,
            "replace_materials": self.deserialize_replace_materials_rule,
        }

        rule_deserializer = rule_deserializers.get(rule_type)

        if not rule_deserializer:
            raise MalformedRule(
                f"Unknown `type` `{rule_type}`, at `{breadcrumb_type}`",
                raw_rule,
                breadcrumb,
            )

        rule = rule_deserializer(raw_rule, breadcrumb)

        return rule

    def deserialize_keep_materials_rule(
        self, raw_rule: Dict[str, JsonValue], breadcrumb: Breadcrumb
    ) -> KeepMaterialsFilterRule:
        # materials (required, non-nullable, no default)
        raw_materials = raw_rule.get("materials")
        breadcrumb_materials = breadcrumb.materials
        if raw_materials is None:
            raise MalformedRule(
                f"Missing `materials`, at `{breadcrumb_materials}`",
                raw_rule,
                breadcrumb_materials,
            )
        if not isinstance(raw_materials, list):
            raise MalformedRule(
                f"Malformed `materials`, at `{breadcrumb_materials}`",
                raw_rule,
                breadcrumb_materials,
            )
        materials = [
            self.material_deserializer.or_location(
                raw_material, breadcrumb_materials[i]
            )
            for i, raw_material in enumerate(raw_materials)
        ]

        return KeepMaterialsFilterRule(materials=materials)

    def deserialize_replace_materials_rule(
        self, raw_rule: Dict[str, JsonValue], breadcrumb: Breadcrumb
    ) -> ReplaceMaterialsFilterRule:
        # materials (required, non-nullable, no default)
        raw_materials = raw_rule.get("materials")
        breadcrumb_materials = breadcrumb.materials
        if raw_materials is None:
            raise MalformedRule(
                f"Missing `materials`, at `{breadcrumb_materials}`",
                raw_rule,
                breadcrumb_materials,
            )
        if not isinstance(raw_materials, list):
            raise MalformedRule(
                f"Malformed `materials`, at `{breadcrumb_materials}`",
                raw_rule,
                breadcrumb_materials,
            )
        materials = [
            self.material_deserializer.or_location(
                raw_material, breadcrumb_materials[i]
            )
            for i, raw_material in enumerate(raw_materials)
        ]

        # replacement (required, non-nullable, no default)
        raw_replacement = raw_rule.get("replacement")
        breadcrumb_replacement = breadcrumb.replacement
        if raw_replacement is None:
            raise MalformedRule(
                f"Missing `replacement`, at `{breadcrumb_replacement}`",
                raw_rule,
                breadcrumb_replacement,
            )
        replacement = self.material_deserializer.or_location(
            raw_replacement, breadcrumb_replacement
        )

        return ReplaceMaterialsFilterRule(materials=materials, replacement=replacement)
