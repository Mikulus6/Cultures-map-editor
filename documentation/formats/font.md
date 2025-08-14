[← index](../index.md)

## Font file `(*.fnt)`

### Introduction

Font file format (`*.fnt`) is an exclusive format for *Cultures* meant for
storing data relevant to fonts used in the game. Unlike regular [fonts](https://en.wikipedia.org/wiki/Font),
which are composed of [vector graphics](https://en.wikipedia.org/wiki/Vector_graphics),
this format uses [raster graphics](https://en.wikipedia.org/wiki/Raster_graphics)
and contains only information about bitmaps without any colormaps, which for
further display requires inheriting such data from additional [`*.pcx`](./picture_exchange.md)
file. Font file format (`*.fnt`) is very similar to more general bitmap file
format ([`*.bmd`](bob_manager_data.md)), which is meant for storing bitmaps
displayable in the game. 

Using `Converters.exe` application provided in [*releases section*](https://github.com/Mikulus6/Cultures-map-editor/releases)
one can freely extract `*.fnt` files to a purely conventional collection of
files with common file types or pack it back into singular `*.fnt` file.

### Conventional extraction

Because of the exact file format specifications for font files, this file
format cannot be directly converted or extracted in any way that would be
objectively correct or historically accurate. Hence, it was decided to use a
purely conventional method to transform stored data into viewable and editable
content. For extracted data, each frame is stored as a [`*.png`](https://en.wikipedia.org/wiki/PNG)
file, for which the number included in the name indicates [ASCII](https://en.wikipedia.org/wiki/ASCII)
value corresponding to given font character texture. Control characters are
excluded, therefore exact [ASCII](https://en.wikipedia.org/wiki/ASCII) value
is shifted by `32`. Additionally `metadata.csv` file contains information
relevant to font display. In the header of this file, value indicating
vertical spacing between lines of text is given. Following content has three
values for each font character. The first is a frame type, which in context of
`*.fnt` files can be reduced to binary indicator of frame presence, while the
two other values indicate how much the texture of the font character should be
shifted horizontally and vertically before being displayed. All units related
to distances are expressed in pixels.

### Modifying

For modifying `*.fnt` files extracted conventionally to `*.csv` and `*.png`
file formats, it is recommended to use [Notepad++](https://notepad-plus-plus.org/)
and [GIMP](https://www.gimp.org/) respectively. Note that the extracted
`*.png` files can contain only monochromatic [RGB](https://en.wikipedia.org/wiki/RGB_color_model)
values and fully transparent pixels.


### File format

For the algorithm used by the provided tools, one can look into the Python
file [*supplements/bitmaps.py*](../../supplements/bitmaps.py) present in this
repository. This file format was first decoded by [Siguza](https://github.com/siguza)
and documented on [XeNTaX forum](https://web.archive.org/web/20210724120011/https://forum.xentax.com/viewtopic.php?t=10705).
Keep in mind, the exact specifications of this algorithm are the same only for
*Cultures: Discovery of Vinland*, *Cultures: The Revenge of the Rain God* and
*Cultures Gold*. There is another slightly different version of this file
format used in *Cultures 2: The Gates of Asgard* and in most of the newer
games released as part of the *Cultures* series.