[← index](../index.md)

## `[Control]`

| Key                | Value type                    | Value meaning                                                                                         |
|:-------------------|:------------------------------|:------------------------------------------------------------------------------------------------------|
| `TextFile`         | string                        | path to `*.ini` file with strings (relative from `Cultures.exe`)                                      |
| `Name`             | integer                       | ID to map title string                                                                                |
| `Creator`          | string                        | string with names of map creators                                                                     |
| `ShortDescription` | string                        | ID to map description string                                                                          |
| `MapIdentifier`    | integer \| integer            | number unique for given map \| map version number                                                     |
| `MapFile`          | string                        | path to `*.map` file with map content                                                                 |
| `PatternIni`       | string                        | path to `.ini` file with `[PatternDef]` sections (relative from `data_v`)                             |
| `TexturePath`      | string                        | path to directory with textures contained in `free` and `sys` subdirectories (relative from `data_v`) |
| `MapSubMode`       | integer                       | map gameplay type (based on final goal)                                                               |
| `NumberOfPlayer`   | integer \| integer            | always `1` \| sum of human and AI players present on map                                              |
| `MapMode`          | integer \| integer \| integer | menu tab for map \| campaign / tutorial ID \| campaign / tutorial mission ID                          |
| `MapPicture`       | string                        | path to `*.pcx` file with map preview (relative from `Cultures.exe`)                                  |
| `CDAudioTrack`     | integer                       | number of music soundtrack                                                                            |

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