# blueprints

> Text-based structures for Minecraft.

# Examples

## Blueprints

Blueprints are a text-based, human-readable/writable structure format. A blueprint compiles-down to a single NBT structure file that can be loaded with a structure block.

Note that all examples use YAML instead of JSON, but the YAML used is 1:1 convertible to/from JSON.

### `demo:bricks`

This first example uses blocks to create a basic structure.

[![image](https://i.imgur.com/0fsLTsp.png)](https://i.imgur.com/yxnoyF1.png)

`data/demo/blueprints/bricks.yaml`

```yaml
# Restrict the size of the structure. Anything larger will cause an error.
size: [5, 5, 5]

# The palette maps characters to different types of palette entries that describe how to
# populate the structure.
palette:
  _:
    type: block
    block: minecraft:air
  f:
    type: block
    block: minecraft:polished_andesite
  c:
    type: block
    block: minecraft:stone_bricks
  o:
    type: block
    block: minecraft:quartz_pillar
  I:
    type: block
    block: minecraft:chiseled_stone_bricks
  X:
    type: block
    block: minecraft:tnt
    state:
      unstable: true
  H:
    # Materials are optional, centralized block definitions.
    type: material
    material: demo:trapped_chest

# The layout is a 2D list of strings (a 3D list of characters) that says how to build
# the structure, piece by piece, using the palette.
layout:
  - - offfo
    - fffff
    - ffXff
    - fffff
    - offfo

  - - o___o
    - _____
    - __I__
    - _____
    - o___o

  - - o___o
    - _____
    - __H__
    - _____
    - o___o

  - - o___o
    - _____
    - _____
    - _____
    - o___o

  - - occco
    - ccccc
    - ccccc
    - ccccc
    - occco
```

### `demo:copper`

This next example uses composition to include another blueprint within itself.

[![image](https://i.imgur.com/vo4pr9X.png)](https://i.imgur.com/KF57IKW.png)

`data/demo/blueprints/copper.yaml`

```yaml
size: [5, 5, 5]

palette:
  # The "B" stands for "base" here, but it can be whatever.
  B:
    type: blueprint
    blueprint: demo:bricks
    # A filter changes the way blocks are included from other blueprints.
    filter: demo:copperize

layout:
  - - B
```

## Blueprint Filters

Filters can be used to change the way blocks are included from other blueprints.

### `demo:copperize`

`data/demo/blueprint_filters/copperize.yaml`

```yaml
# Replace one block with another block.
- type: replace_block
  input: minecraft:polished_andesite
  output: minecraft:minecraft:cut_copper
- type: replace_block
  input: minecraft:stone_bricks
  output: minecraft:minecraft:cut_copper
- type: replace_block
  input: minecraft:quartz_pillar
  output: minecraft:copper_block
# Keep only the listed blocks, discarding the rest.
- type: keep_blocks
  blocks:
    - minecraft:air
    - minecraft:copper_block
    - minecraft:cut_copper
```

## Materials

Materials are centralized, reusable block definitions that can be managed from one place.

### `demo:trapped_chest`

`data/demo/materials/trapped_chest.yaml`

```yaml
block: minecraft:trapped_chest
nbt:
  Items:
    - id: minecraft:diamond
      Count: 1b
      Slot: 13b
```
