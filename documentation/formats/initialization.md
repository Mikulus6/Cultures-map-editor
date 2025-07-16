[← index](../index.md)

## Initialization file `(*.ini)`

### Introduction

[Initialization files](https://en.wikipedia.org/wiki/INI_file) are a common
type of file, which is not exclusive to *Cultures* video games. However,
syntax-related details are exclusive and vary from regular `*.ini` files
outside the game's directories. This file type stores plain text and is
bidirectionally interchangeable with `*.cif` file type. Using `Converters.exe`
application provided in the [*releases section*](https://github.com/Mikulus6/Cultures-map-editor/releases)
one can freely encrypt `*.ini` files or decrypt `*.cif` files.

### Syntax

Initialization files can be divided into separate clusters of data known as
_sections_. Each section consists of a name and an implicit index. This index
is not directly visible but depends on how many sections with the same name
were declared previously. Therefore, unlike in external `*.ini` files, there
can be multiple sections with the same name, and game will differentiate
between them based on implicit index. Sections can be declared using square
brackets between which the name of section is written. To be exact, line in
which the section is declared must start with `[` character and end with `]`
character. Between these characters, the name of the section must be declared.
After such line with section declaration, all further lines are considered the
content of this section until the next section is declared.

Data included in every section can be divided into one-line portions of data
known as *entries*. Each entry can be thought of as an item of dictionary with
given key and ordered list of values. However, similarly to sections, there can
be multiple entries with the same key, and they will be differentiated based on
the order of entries declarations in the section. The key of an entry should
consist only of lowercase and uppercase letters of Latin alphabet. It is written
at the beginning of every line inside all sections. Then, separated by spaces,
a single value or multiple values are declared. The order of keys and values
are significant for various purposes.

Values in entries have one of three specified data types. These data types
are: *float*, *integer* and *string*. Syntax related to value declaration of
each mentioned data type is consistent with [C++](https://en.wikipedia.org/wiki/C++).
Floating point representation is dot (`.`) character and strings are enclosed
by quotation marks (`"`).

### Example

Below is the exemplary content of arbitrary `*.ini` file with syntax specific
to *Cultures*. Meaning of present names and values is purely for syntax
explanation and is not representing the actual content of real files related
to discussed game.

```ini
[vehicle]
type "car"
size 50 10 25
[animal]
type "dog"
speed 20.0
[animal]
type "cat"
speed 10.0
```

There are three sections in provided example with respective names being
`vehicle`, `animal` and `animal`. First section with name `vehicle` has two
entries. First entry has key `type` and string value `"car"`. Second entry in
this section has key `size` and three ordered integer values `50`, `10` and
`25`. Next sections are named `animal` and also have two entries. First entry
has key `type` and string value `"dog"` or `"cat"`. Second value has the key
`speed` and float value `20.0` or `10.0`.

For practical `*.ini` files used by game, one must extract `*.lib` archives
and decode `*.cif` files present in them. These procedures are described in
documentation related to `*.lib` and `*.cif` file types respectively.

### Encoding

When writing non-[ASCII](https://en.wikipedia.org/wiki/ASCII) characters in
`*.ini` files it is important to use [Windows-1252](https://en.wikipedia.org/wiki/Windows-1252)
encoding, which is not compatible with widely used [Unicode](https://en.wikipedia.org/wiki/Unicode)
or [UTF-8](https://en.wikipedia.org/wiki/UTF-8). Therefore, it is recommended
to use [Notepad++](https://notepad-plus-plus.org/downloads/) and manually
change encoding in option `Encoding > Character sets > Western European > Windows-1252`.
This functionality is usually not accessible in the default preinstalled text
editors on commonly used operating systems.

Note that the exact encoding might differ for specific language editions
other than the most popular English and German versions of the game. However,
it is common for *Cultures* to use constant number of bytes per character
which excludes [Unicode](https://en.wikipedia.org/wiki/Unicode) and [UTF-8](https://en.wikipedia.org/wiki/UTF-8)
from being widely used in translations.