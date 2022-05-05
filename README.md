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

See the [examples](#examples) and the [test packs] for reference.

## Options

### `data_version`

> Default: `3095` (22w18a)

The data version corresponding to the [version of the game](https://minecraft.fandom.com/wiki/Data_version#List_of_data_versions) being targeted.

### `output_location`

> Default: `"{namespace}:{path}"`

The final output location of each structure, relative to the blueprint's original `namespace` and `path`.

## Examples

All examples use YAML instead of JSON, but the YAML used is 1:1 convertible to/from JSON.

See the [test packs] for a complete set of examples.

This first example uses basic blocks to create a simple structure.

![image](https://user-images.githubusercontent.com/1885643/118862799-20da5f80-b8ac-11eb-9ad3-23b50f251e32.png)

https://github.com/Arcensoth/blueprints/blob/main/tests/fleecy_box/src/data/fleecy_box/blueprints/templates/base.yaml

This next example uses composition and a filter to include a modified version of another template.

![image](https://user-images.githubusercontent.com/1885643/118862891-3c456a80-b8ac-11eb-94a7-763484c12069.png)

https://github.com/Arcensoth/blueprints/blob/main/tests/fleecy_box/src/data/fleecy_box/blueprints/templates/copper.yaml

Note the use of a filter: these can be used to change the way blocks are included from other templates.

https://github.com/Arcensoth/blueprints/blob/main/tests/fleecy_box/src/data/fleecy_box/blueprints/filters/copperize.yaml

[logo]: ./logo.png
[package-badge]: https://img.shields.io/pypi/v/mcblueprints.svg
[version-badge]: https://img.shields.io/pypi/pyversions/mcblueprints.svg
[style-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[test packs]: https://github.com/Arcensoth/blueprints/tree/main/tests
