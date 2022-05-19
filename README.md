![logo]

# Blueprints

> Text-based structures for Minecraft.

[![package-badge]](https://pypi.python.org/pypi/mcblueprints/)
[![version-badge]](https://pypi.python.org/pypi/mcblueprints/)
[![style-badge]](https://github.com/ambv/black)

Blueprints are a text-based structure format for Minecraft optimized for human-readability. A blueprint compiles-down to a single NBT structure file that can be loaded with a structure block or a jigsaw block.

Here are some reasons you may want to use blueprints:

- They can be diff'd and _properly_ included in version control, unlike their NBT equivalent.
- They are far smaller and less repetitive than their SNBT equivalent, which is often used for version control.
- They can be expressed purely through text, without having to think about the underlying structure format (and without having to open the game).
- They can be updated to (and optimized for) a newer version of the game, just by re-compiling them with a newer data version.
- They have the potential to take up significantly less space than their NBT equivalent, for codebases that take advantage of composition.

Keep in mind that - although they are optimized for human-readbility - blueprints aren't nearly as "hands-on" as editing structures in-game. There are pros and cons to either approach, and the case for blueprints should be weighed carefully based on project size and complexity.

## Usage

Blueprints are created and maintained in the same way as vanilla resources, but under a made-up `blueprints` folder with several sub-folders.

**Blueprints are currently only available through a [beet] plugin.**

See the [examples](#examples) for reference.

## Options

### `data_version`

> Default: `2975` (1.18.2)

The data version corresponding to the [version of the game](https://minecraft.fandom.com/wiki/Data_version#List_of_data_versions) being targeted.

### `output_location`

> Default: `"{namespace}:{path}"`

The final output location of each structure, relative to the blueprint's original `namespace` and `path`.

## Examples

All examples use YAML instead of JSON, but the YAML used is 1:1 convertible to/from JSON.

See the [example packs] for a complete set of examples.

### `fleecy_box:base`

`fleecy_box:base` uses basic blocks to create a simple structure.

![image](https://user-images.githubusercontent.com/1885643/169146097-16a39981-0921-4c98-a96f-b6d3d4d695db.png)

> [data/fleecy_box/blueprints/templates/base.yaml](./examples/fleecy_box/src/data/fleecy_box/blueprints/templates/base.yaml)

```yaml
# Optionally restrict the size of the structure. An error will be raised if anything
# extends outside of these bounds. This goes by (x, y, z) or (length x height x width).
# Omitting this field will cause the structure to "shrink wrap" when it is generated,
# taking on a minimal size.
size: [5, 5, 5]

# The palette maps characters to different types of palette entries that describe how to
# populate the structure. These can be blocks as well as other layouts. Note that spaces
# and dots `.` are automatically treated as void space and excluded from the structure.
palette:
  # Basic blocks are permitted in string form.
  _: minecraft:air
  g: minecraft:glass
  c: minecraft:glowstone
  b: minecraft:bricks
  # To define block states, use the block type entry.
  P:
    type: block
    block:
      name: minecraft:quartz_pillar
      state:
        axis: "y"
  X:
    type: block
    block:
      name: minecraft:tnt
      state:
        unstable: true
  # To define NBT data, use the block type entry.
  T:
    type: block
    block:
      name: minecraft:trapped_chest
      data:
        Items:
          - id: minecraft:diamond
            Count: 1b
            Slot: 13b

# The layout can be either a multi-line string, or a 2-D list of strings (a 3-D list of
# characters) that says how to build the structure, piece by piece, using the palette.
# Note that the first section of the layout corresponds to the top-most layer of blocks
# in the structure.
layout: |
  ggggg
  ggggg
  ggggg
  ggggg
  ggggg

  ggggg
  g___g
  g___g
  g___g
  ggggg

  ggggg
  g___g
  g_T_g
  g___g
  ggggg

  cgggc
  g___g
  g_P_g
  g___g
  cgggc

  bbbbb
  bbbbb
  bbXbb
  bbbbb
  bbbbb
```

### `fleecy_box:copper`

`fleecy_box:copper` uses composition and a filter to include a modified version of `fleecy_box:base`.

![image](https://user-images.githubusercontent.com/1885643/169146022-9058443d-5926-4ac0-901a-75517828f73f.png)

> [data/fleecy_box/blueprints/templates/copper.yaml](./examples/fleecy_box/src/data/fleecy_box/blueprints/templates/copper.yaml)

```yaml
# Make sure to account for any included structures in the final structure.
size: [5, 5, 5]

palette:
  # Templates are composable. They can be included within one another, and the final
  # structure will be a flattened version with a minimal palette.
  B:
    type: template
    template: fleecy_box:base
    # A filter changes the way blocks are included from other templates.
    filter: fleecy_box:copperize

layout:
  - - B
```

### `fleecy_box:copperize`

Note the use of the `fleecy_box:copperize` filter in `fleecy_box:copper`: these can be used to change the way blocks are included from other templates.

> [data/fleecy_box/blueprints/filters/copperize.yaml](./examples/fleecy_box/src/data/fleecy_box/blueprints/filters/copperize.yaml)

```yaml
# Replace certain blocks with another block.
- type: replace
  replace:
    - minecraft:bricks
    - minecraft:tnt
  replacement: minecraft:cut_copper
- type: replace
  replace:
    - minecraft:glowstone
    - minecraft:quartz_pillar
  replacement: minecraft:copper_block
- type: replace
  replace:
    - minecraft:trapped_chest
  replacement: minecraft:beacon

# Keep only certain blocks, discarding the rest.
- type: keep
  keep:
    - minecraft:copper_block
    - minecraft:cut_copper
    - minecraft:beacon
```

[beet]: https://github.com/mcbeet/beet
[example packs]: ./examples
[logo]: ./logo.png
[package-badge]: https://img.shields.io/pypi/v/mcblueprints.svg
[style-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[version-badge]: https://img.shields.io/pypi/pyversions/mcblueprints.svg
