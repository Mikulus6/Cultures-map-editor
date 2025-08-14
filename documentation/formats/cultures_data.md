[← index](../index.md)

## Cultures data file (`*.cdf`)

### Introduction

Cultures data file (`*.cdf`) is a file format used by *Cultures*, meant for
storing raw binary data. This file format does not have any coherent internal
structure which would make it easily readable. One can use hexadecimal editor
of choice to open and modify this type of file. Files with this format are
mostly leftovers from the development process and are not relevant to the way
the game works.

### Existing usages

There exist four instances of `*.cdf` files in `data_v` directory which can be
extracted from `data_l\data_v.lib` library. These are:

| File name                      | Parent directory                 | Important |
|--------------------------------|----------------------------------|-----------|
| `z_animation_descriptions.cdf` | `data_v\ve_graphics\creatures`   | No        |
| `landscapedefs.cdf`            | `data_v\ve_graphics\landscape`   | No        |
| `patterndefs_normal.cdf`       | `data_v\ve_graphics\pattern1`    | No        |
| `remaptables.cdf`              | `data_v\ve_graphics\remaptables` | Yes       |

First three of these files store information which is almost entirely
duplicated from `*.cif` files present in the same parent directories with the
same base name. The exception to that is `remaptables.cdf` file, the internal
structure of which corresponds to an archive. Hence, this one particular file
can be extracted to the set of `*.pcx` files and packed back. However, it is
not as generic as `*.lib` file format. Only `*.pcx` files with a colormap of
`256` colors and a bitmap with size `16`×`16` can be stored within this file.
Moreover, `remaptables.cif` is required in order to correctly extract or pack
back the content from this one `*.cdf` file, as it provides necessary
information about filenames and subdirectories.

### File format

For the algorithms used to read this files, one can look into the Python
module [*supplements.py*](../../supplements) present in this repository. Using
`Converters.exe` application provided in [*releases section*](https://github.com/Mikulus6/Cultures-map-editor/releases)
one can extract and pack back `remaptables.cdf`. One can additionally verify
cohesion between `*.cif` and `*.cdf` files by running appropriate scripts
present in the aforementioned module.