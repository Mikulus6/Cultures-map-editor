[← index](index.md)

## `[Control]`
| Key                | Value type                 | Value meaning                                                                                         |
|:-------------------|:---------------------------|:------------------------------------------------------------------------------------------------------|
| `TextFile`         | text                       | path to `*.ini` file with strings (relative from `Cultures.exe`)                                      |
| `Name`             | number                     | ID to map title string                                                                                |
| `Creator`          | text                       | string with names of map creators                                                                     |
| `ShortDescription` | text                       | ID to map description string                                                                          |
| `MapIdentifier`    | number \| number           | number unique for given map \| map version number                                                     |
| `MapFile`          | text                       | path to `*.map` file with map content                                                                 |
| `PatternIni`       | text                       | path to `.ini` file with `[PatternDef]` sections (relative from `data_v`)                             |
| `TexturePath`      | text                       | path to directory with textures contained in `free` and `sys` subdirectories (relative from `data_v`) |
| `MapSubMode`       | number                     | map gameplay type (based on final goal)                                                               |
| `NumberOfPlayer`   | number \| number           | always `1` \| sum of human and AI players present on map                                              |
| `MapMode`          | number \| number \| number | menu tab for map \| campaign / tutorial ID \| campaign / tutorial mission ID                          |
| `MapPicture`       | text                       | path to `*.pcx` file with map preview (relative from `Cultures.exe`)                                  |
| `CDAudioTrack`     | number                     | number of music soundtrack                                                                            |

### `MapSubMode`

| map gameplay type | Value meaning                       |
|:-----------------:|:------------------------------------|
|        `0`        | deathmatch mode map (kill player)   |
|        `1`        | economy mode map (collect goods)    |
|        `2`        | economy mode map (reach population) |

### `MapMode`

This key has more than one number as value if and only if value of first argument is set to `1`. 

| menu tab for map | Value meaning                                                    |
|:----------------:|:-----------------------------------------------------------------|
|       `1`        | *Single player* > *Tutorial* or *Single player* > *New Campaign* |
|       `2`        | *Single player* > *New scenario*                                 |
|       `3`        | *Single player* > *For beginners*                                |
|       `4`        | *Multiplayer*                                                    |

| campaign / tutorial ID | Value meaning                                                    |
|:----------------------:|:-----------------------------------------------------------------|
|          `0`           | *Single player* > *Tutorial*                                     |
|          `1`           | *Single player* > *New Campaign* > *Discovery of Vinland*        |
|          `2`           | *Single player* > *New Campaign* > *The Revenge of the Rain God* |