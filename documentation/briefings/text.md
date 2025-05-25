[← index](../index.md)

## Briefings keywords

| Keyword            | Meaning                                                                                                                                                                                                                                                            |
|:-------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `font`             | For a given number loads the corresponding font.                                                                                                                                                                                                                   |
| `color`            | For a given number loads the corresponding color.                                                                                                                                                                                                                  |
| `picture`          | For a given number displays the corresponding picture. (Always centered)                                                                                                                                                                                           |
| `userpicture`      | For a given number displays a square representing specific player and his diplomatic status. Player is determined by subtracting 100 from the given number.                                                                                                        |
| `icon`             | For a given number displays the corresponding picture. (Aligned as specified)                                                                                                                                                                                      |
| `anchor`           | Creates an invisible anchor point with the given number for jumping to the specified line of text.                                                                                                                                                                 |
| `localjump`        | One number is given. Further text is a clickable hyperlink. Upon clicking it, text jumps to the given anchor point in the current briefing.                                                                                                                        |
| `block`            | For a given number loads the corresponding text alignment.                                                                                                                                                                                                         |
| `include`          | For a given `*.txt` file path relative to `Cultures.exe` includes it as part of the briefing. Displaying included text takes into account text formatting.                                                                                                         |
| `includetext`      | For a given `*.txt` file path relative to `Cultures.exe` includes it as part of the briefing. Displaying included text does not take into account text formatting.                                                                                                 |
| `rem`              | Comment skipped when rendering briefings.                                                                                                                                                                                                                          |
| `globaljump`       | Three numbers with leading zeros are given as `XXX,XXXXXX,XX`, where `X` is any decimal digit. Further text is a clickable hyperlink. Upon clicking it, briefing `data_m\c1_txt\c1_fhll\txt_XXXXXX.txt` is being opened and text jumps to given anchor point `XX`. |
| `onscreencallback` | Three numbers with leading zeros are given as `X,XXXXXX,X`, where `X` is any decimal digit. If first number is equal to `1`, then the sound file `data_v\ve_soundfx\briefings\XXXXXX.mp3` will be played.                                                          |
| `setdatafileid`    | For given number (without leading zeros) reads `data_m\c1_txt\c1_fhll\data_XXX.cif` file, where `XXX` are any three decimal digits, then uses it as a reference for external briefing parameters.                                                                  |
| `textxstart`       | For given number sets the minimum horizontal value starting from which text can be displayed.                                                                                                                                                                      |
| `textxend`         | For given number sets the maximum horizontal value past which text will be warped to the next line.                                                                                                                                                                |

### `block`
| Value | Text alignment |
|:------|:---------------|
| `0`   | left           |
| `1`   | justify        |
| `2`   | center         |
| `3`   | right          |

### Keys in files referenced by `setdatafileid`
Keys stated in following section are referenced in `*.txt` files via keywords
`font`, `color`, `picture`, `icon`, `localjump` and `globaljump`. Note that
the name of section is absent here, which is  an exception from standard
`*.ini` file format.

| Key             | Value type        | Arguments                                               |
|:----------------|:------------------|---------------------------------------------------------|
| `color`         | integer \| string | key \| path to `*.pcx` file relative to `Cultures.exe`  |
| `highlitecolor` | integer \| string | key \| path to `*.pcx` file relative to `Cultures.exe`  |
| `font`          | integer \| string | key \| path to `*.fnt` file relative to `Cultures.exe`  |
| `bitmap`        | integer \| string | key \| path to `*.pcx` file  relative to `Cultures.exe` |