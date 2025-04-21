[← index](../index.md)

## Cultures initialization file `(*.cif)`

### Introduction

Cultures initialization file `(*.cif)` is a file format used by *Cultures*
meant for storing textual data. Content of this file format is protected by
cipher. Breaking it makes it possible to losslessly convert this type of file
to plain text stored as `*.ini` file. Applying this cipher on decrypted file
also makes it possible to losslessly convert it back to original file format.
In short this means `*.cif` and `*.ini` file formats are bidirectionally
interchangeable.

Using `Converters.exe` application provided in [*releases section*](https://github.com/Mikulus6/Cultures-map-editor/releases)
one can freely decrypt `*.cif` files or encrypt `*.ini` files. Historically,
[*cif2txt.exe*](https://web.archive.org/web/20210724220815/https://forum.xentax.com/viewtopic.php?t=3711)
was used to partially preform these convertions and had further backward
compatibility for old operating systems, but is neither recommended anymore nor
easily available online.

### Inclusion priority

// how game reads cif and ini, priority etc


### File format

// credit bacter here

[ASCII](https://en.wikipedia.org/wiki/ASCII)-based [Caesar cipher](https://en.wikipedia.org/wiki/Caesar_cipher)
combined with [XOR cipher](https://en.wikipedia.org/wiki/XOR_cipher)

