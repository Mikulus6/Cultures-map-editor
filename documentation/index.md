[← readme](../readme.md)

# Documentation

## Introduction

Main application `Editor.exe` present in [*releases section*](https://github.com/Mikulus6/Cultures-map-editor/releases)
provides functionalities necessary to view and modify `*.map` files. This is
enough to freely manipulate terrain, heightmap, landscapes and structures but
not enough to create a fully playable map in game on its own. For this, one
has to construct additional text and image files which, combined with `*.map`
file, can contribute to playable content. These are `*.cif`, `*.pcx` and
`.txt` files. The following documentation is meant to explain how these
additional files are constructed and how to properly modify them.

There are required third-party programs meant for modifying those
files. These are listed below. User is expected to have them installed
alongside `Converters.exe` supplement provided in [*releases section*](https://github.com/Mikulus6/Cultures-map-editor/releases).
Default text and image editors present on commonly known operating systems
might not have enough functionalities, as it might be necessary to manually
change text encoding and to modify a bitmap with indexed colormap.

## Compendium

### External programs

 - [Notepad++](https://notepad-plus-plus.org/)
 - [GIMP](https://www.gimp.org/)

### File formats

- [`*.cif` Cultures initialization file](formats/cultures_initialization.md)
- [`*.ini` Initialization file]()
- [`*.lib` Library](formats/library.md)
- [`*.pcx` Picture exchange]()
- [`*.txt` Text file]()

### Sections

 - [Control](sections/control.md)
 - [AI](sections/ai.md)
 - [StartUp](sections/startup.md)
 - [Mission](sections/mission.md)
 - [text](sections/text.md)