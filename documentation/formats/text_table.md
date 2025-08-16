[← index](../index.md)

## Text table (`*.sal` / `*.tab`)

### Introduction

Text table file (`*.sal` / `*.tab`) is a file format used by *Cultures*,
meant for storing textual data. Content of this file format is protected by a
cipher. Breaking it makes it possible to losslessly convert this type of file
to plain text stored as a `*.txt` file. Applying this cipher to a decrypted
file also makes it possible to losslessly convert it back to original file
format. This file format is very similar to [`*.cif`](cultures_initialization.md)
file format, however it does not come with the convenience of any direct
inclusion of `*.txt` files by the game, unlike with `*.cif` and `*.ini` files.

### Newline representation

Text table, as the name suggests, contains a one-dimensional table of strings.
These strings themselves can contain newline characters. Therefore, when
representing this one-dimensional table as a text file where each line of text
corresponds to one cell in a table, it is necessary to distinguish between
newline characters that are meant to be stored as part of entries, and
newline characters that are meant to separate entries between each other.
Due to such inconvenience, it has been decided, purely by convention, that
newline characters which are meant to be part of an entry, ought to be written
as the `\r\n` sequence of characters.

### File format

For the algorithm used by the provided tools, one can look into the Python
file [`supplements/initialization.py`](../../supplements/initialization.py)
present in this repository. Cipher present in `*.tab` and `*.sal` files uses
an [ASCII](https://en.wikipedia.org/wiki/ASCII)-based
[Caesar cipher](https://en.wikipedia.org/wiki/Caesar_cipher) combined with
[XOR cipher](https://en.wikipedia.org/wiki/XOR_cipher). This cipher was
first broken by Bacter and documented on
[XeNTaX forum](https://web.archive.org/web/20210724220815/https://forum.xentax.com/viewtopic.php?t=3711).
