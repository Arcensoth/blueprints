![logo]

# Blueprints

> Text-based structures for Minecraft.

[![package-badge]](https://pypi.python.org/pypi/blueprints/)
[![version-badge]](https://pypi.python.org/pypi/blueprints/)
[![style-badge]](https://github.com/ambv/black)

Blueprints are a text-based structure format for Minecraft optimized for human-readability. A blueprint compiles-down to a single NBT structure file that can be loaded with a structure block.

Here are some reasons you may want to use blueprints:

- They can be diff'd and _properly_ included in version control, unlike their NBT equivalent.
- They are far smaller and less repetitive than their SNBT equivalent, which is often used for version control.
- They can be expressed purely through text, without having to think about the underlying structure format (and without having to open the game).
- They can be updated to (and optimized for) a newer version of the game, just by re-running the CLI with the `--data_version` argument.
- They have the potential to take up significantly less space than their NBT equivalent, for codebases that take advantage of composition.

## Usage

Blueprints are created and maintained in the same way as vanilla resources, but under a made-up `blueprints` folder.

See the [examples] and the [demo pack](https://github.com/Arcensoth/blueprints/tree/main/tests/datapacks/demo-datapack/data) for reference.

The most basic invocation of the CLI looks like this:

```bash
python -m blueprints build --input path/to/input/pack --output path/to/output/pack --data_version 2715
```

- `--input` is the path to the input pack. This is where your blueprints reside.
- `--output` is the path to the output pack. This is where the generated structures files will be placed. This can be the same as the input pack, but beware of overwriting existing files.
- `--data_version` is required and `2715` should be replaced with the [version of the game](https://minecraft.fandom.com/wiki/Data_version#List_of_data_versions) you are targeting.

Run `python -m blueprints build --help` for a complete list of options.

## Examples

All examples use YAML instead of JSON, but the YAML used is 1:1 convertible to/from JSON.

See the full [demo pack](https://github.com/Arcensoth/blueprints/tree/main/tests/datapacks/demo-datapack/data) for a complete set of examples.

This first example uses basic blocks to create a simple structure.

![image](https://user-images.githubusercontent.com/1885643/118862799-20da5f80-b8ac-11eb-9ad3-23b50f251e32.png)

**`fleecy_box:base`**

[`data/fleecy_box/blueprints/base.yaml`](https://github.com/Arcensoth/blueprints/blob/main/tests/datapacks/demo-datapack/data/fleecy_box/blueprints/base.yaml)

```yaml
# Restrict the size of the structure. An error will be raised if anything extends
# outside of these bounds. This goes by (x, y, z) or (length x height x width).
size: [5, 5, 5]

# The palette maps characters to different types of palette entries that describe how to
# populate the structure. These can be blocks as well as other blueprints.
palette:
  # Strings are assumed to be basic blocks.
  _: minecraft:air
  g: minecraft:glass
  c: minecraft:glowstone
  b: minecraft:bricks
  # To define block states, use the block type entry.
  P:
    type: block
    name: minecraft:quartz_pillar
    state:
      axis: y
  X:
    type: block
    name: minecraft:tnt
    state:
      unstable: true
  # To define NBT data, use the block type entry.
  T:
    type: block
    name: minecraft:trapped_chest
    data:
      Items:
        - id: minecraft:diamond
          Count: 1b
          Slot: 13b

# The layout is a 2-D list of strings (a 3-D list of characters) that says how to build
# the structure, piece by piece, using the palette. Note that the first section of the
# layout corresponds to the top-most layer of blocks in the structure.
layout:
  - - ggggg
    - ggggg
    - ggggg
    - ggggg
    - ggggg

  - - ggggg
    - g___g
    - g___g
    - g___g
    - ggggg

  - - ggggg
    - g___g
    - g_T_g
    - g___g
    - ggggg

  - - cgggc
    - g___g
    - g_P_g
    - g___g
    - cgggc

  - - bbbbb
    - bbbbb
    - bbXbb
    - bbbbb
    - bbbbb
```

This next example uses composition and a filter to include a modified version of another blueprint.

![image](https://user-images.githubusercontent.com/1885643/118862891-3c456a80-b8ac-11eb-94a7-763484c12069.png)

**`fleecy_box:copper`**

[`data/fleecy_box/blueprints/copper.yaml`](https://github.com/Arcensoth/blueprints/blob/main/tests/datapacks/demo-datapack/data/fleecy_box/blueprints/copper.yaml)

```yaml
# Make sure to account for any included structures in the final structure.
size: [5, 5, 5]

palette:
  # Blueprints are composable. They can be included within one another, and the final
  # structure will be a flattened version with a minimal palette.
  B:
    type: blueprint
    blueprint: fleecy_box:base
    # A filter changes the way blocks are included from other blueprints.
    filter: fleecy_box:copperize

layout:
  - - B
```

Note the use of a filter: these can be used to change the way blocks are included from other blueprints.

**`fleecy_box:copperize`**

[`data/fleecy_box/filters/copperize.yaml`](https://github.com/Arcensoth/blueprints/blob/main/tests/datapacks/demo-datapack/data/fleecy_box/filters/copperize.yaml)

```yaml
# Replace one block with another block.
- type: replace_blocks
  blocks:
    - minecraft:bricks
  replacement: minecraft:cut_copper

- type: replace_blocks
  blocks:
    - minecraft:glowstone
    - minecraft:quartz_pillar
  replacement: minecraft:copper_block

# Keep only the listed blocks, discarding the rest.
- type: keep_blocks
  blocks:
    - minecraft:copper_block
    - minecraft:cut_copper
```

[logo]: ./logo.png
[package-badge]: https://img.shields.io/pypi/v/blueprints.svg
[version-badge]: https://img.shields.io/pypi/pyversions/blueprints.svg
[style-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
