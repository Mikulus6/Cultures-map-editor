[← index](../index.md)

## Bob manager data (`*.bmd`)

### Introduction

Bob manager data (`*.bmd`) is an exclusive format for *Cultures* meant for
storing data relevant to [blitter objects](https://en.wikipedia.org/wiki/Blitter_object)
used in the game. This format uses [raster graphics](https://en.wikipedia.org/wiki/Raster_graphics)
and contains only information about bitmaps without any colormaps, which for
further display requires inheriting such data from an additional [`*.pcx`](./picture_exchange.md)
file. Bob manager data file format (`*.bmd`) is very similar to more specific
font file format ([`*.fnt`](font.md)), which is meant for storing fonts
displayable in the game. Note that more than one bitmap can be stored in a
single bob manager data file.

Using `Converters.exe` application provided in [releases section](https://github.com/Mikulus6/Cultures-map-editor/releases)
one can freely extract `*.bmd` files to a purely conventional collection of
files with common file types or pack them back into singular `*.bmd` file.

### Conventional extraction

Because of the exact file format specifications for `*.bmd` files, this file
format cannot be directly converted or extracted in any way that would be
objectively correct or historically accurate. Hence, it was decided to use a
purely conventional method to transform stored data into viewable and editable
content. For extracted data, each frame is stored as a [`*.png`](https://en.wikipedia.org/wiki/PNG)
file. Additionally `metadata.csv` file contains information relevant to bitmap
display. The content of this file has three values for each bitmap. The first
is a frame type, while the two other values indicate how much the bitmap
should be shifted horizontally and vertically before being displayed. All
units related to distances are expressed in pixels.

### Frame type

Frame type is a numerical value indicating the exact purpose of given frame
contained within blitter object. This value is an integer ranging from `0` to
`3`. The table below explains for what goal given value is being used in the
game. All numerical values of pixels present on bitmaps should be interpreted
as unsigned bytes. This value is represented by brightness of the given pixel.

| Frame type | Meaning                                                                                                                           |           Example            |
|:----------:|-----------------------------------------------------------------------------------------------------------------------------------|:----------------------------:|
|    `0`     | Frame has size `0`×`0` and does not contain any additional information.                                                           |              -               |
|    `1`     | Frame contains regular bitmap. Numerical values of pixels correspond to indices of colormap.                                      | ![1](../assets/frames/1.png) |
|    `2`     | Frame contains binary bitmap representing shape of shadow.                                                                        | ![2](../assets/frames/2.png) |
|    `3`     | Frame contains bitmap in which numerical values indicate how late in building process should given pixel of house texture appear. | ![3](../assets/frames/3.png) |



### Modifying

For modifying `*.bmd` files extracted conventionally to `*.csv` and `*.png`
file formats, it is recommended to use [Notepad++](https://notepad-plus-plus.org/)
and [GIMP](https://www.gimp.org/) respectively. Note that the extracted
`*.png` files can contain only monochromatic [RGB](https://en.wikipedia.org/wiki/RGB_color_model)
values and fully transparent pixels.

### File format

For the algorithm used by the provided tools, one can look into the Python
file [`supplements/bitmaps.py`](../../supplements/bitmaps.py) present in this
repository. This file format was first decoded by [Siguza](https://github.com/siguza)
and documented on [XeNTaX forum](https://web.archive.org/web/20210724120011/https://forum.xentax.com/viewtopic.php?t=10705).
Keep in mind, the exact specifications of this algorithm are the same only for
*Cultures: Discovery of Vinland*, *Cultures: The Revenge of the Rain God* and
*Cultures Gold*. There is another slightly different version of this file
format used in *Cultures 2: The Gates of Asgard* and in most of the newer
games released as part of the *Cultures* series.