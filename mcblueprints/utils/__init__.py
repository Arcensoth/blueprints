from typing import Any, Mapping, cast


def is_submapping(subdict: Mapping[str, Any], superdict: Mapping[str, Any]) -> bool:
    sub_items = subdict.items()
    super_items = superdict.items()
    return all((item in super_items) for item in sub_items)


def charmap_from_list(value: list[Any]) -> list[list[str]]:
    charmap: list[list[str]] = []

    for i, raw_layer in enumerate(reversed(value)):
        if raw_layer is None:
            charmap.append([])
            continue

        if isinstance(raw_layer, str):
            raw_layer = list(raw_layer)

        if not isinstance(raw_layer, list):
            raise ValueError(
                f"Expected layer {i} to be a `str` or `list`, but got: {raw_layer}"
            )

        raw_layer = cast(list[Any], raw_layer)

        layer: list[str] = []

        for j, raw_row in enumerate(raw_layer):
            if raw_row is None:
                layer.append("")
                continue

            if not isinstance(raw_row, str):
                raise ValueError(
                    f"Expected row {j} in layer {i} to be a `str`, but got: {raw_row}"
                )

            layer.append(raw_row)

        charmap.append(layer)

    return charmap


def charmap_from_str(value: str) -> list[list[str]]:
    charmap: list[list[str]] = []
    layer: list[str] = []
    for line in value.splitlines():
        if line:
            layer.append(line)
        else:
            charmap.append(layer)
            layer = []
    charmap.append(layer)
    return list(reversed(charmap))
