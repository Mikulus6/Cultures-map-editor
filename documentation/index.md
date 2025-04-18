[← readme](../readme.md)

# Documentation

[*Cultures Map Editor*](https://github.com/Mikulus6/Cultures-map-editor)
provides functionalities necessary to view and modify `*.map` files. This is
enough to freely manipulate terrain, heightmap, landscapes and structures but
not enough to create a fully playable map in game. For this, one has to
construct additional text and image files which combined with `*.map` file can
contribute to playable content. These are `*.cif`, `*.pcx` and `.txt` files.
Following documentation is meant to explain how these additional files are
constructed and how to properly modify them.

There are required third party applications meant for modifying those
filetypes. These are [*Notepad++*](https://notepad-plus-plus.org/) and
[*GIMP*](https://www.gimp.org/). User is expected to have them installed
alongsite `Converters.exe` supplement provided in [*releases section*](https://github.com/Mikulus6/Cultures-map-editor/releases).
Default text and image editors present on commonly known operating systems
might not have enough functionalities, as it might be necessary to manually
change text encoding and to modify bitmap with indexed colormap.
It is assumed that user has basic knowledge of how to manipulate files and
directories via file explorer of choice and knows how to modify text or image files.

### File formats

- [`*.lib` Library](formats/library.md)
- [`*.cif` Cultures initialization file]()
- [`*.ini` Initialization file]()
- [`*.pcx` Picture exchange]()
- [`*.txt` Text file]()

### Sections

 * [Control](sections/control.md)
 * [AI](sections/ai.md)
 * [StartUp](sections/startup.md)
 * [Mission](sections/mission.md)
 * [text](sections/text.md)