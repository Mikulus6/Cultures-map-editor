[← index](../index.md)

## `[Mission]`

| Key           | Value type         | Arguments                                        | Arguments meaning                                          |
|:--------------|--------------------|:-------------------------------------------------|:-----------------------------------------------------------|
| `StartText`   | integer            | cutscene ID                                      | cutscene played when mission becomes active                |
| `StartTime`   | integer            | seconds                                          | duration from start before mission is checked (in seconds) |
| `Text`        | integer            | cutscene ID                                      | cutscene played when mission becomes complete              |
| `Name`        | string             | mission name                                     | mission name used as a textual ID in other missions        |
| `Type`        | integer            | mission type                                     | mission initial activity state and completion quantifier   |
| `AddGoal`     | integer \| *       | goal type \| * miscellaneous goal parameters     | mission goal (see [`AddGoal`](#AddGoal) for details)       |
| `AddResult`   | integer \| *       | result type \| * miscellaneous result parameters | mission result (see [`AddResult`](#AddResult) details)     |
| `SetGoalText` | integer \| integer | sub-goal index \| string ID                      | goal text visible in mission briefings menu in game        |

### `StartText` `Text`

|     cutscene ID      | Value meaning                                                                                              |
|:--------------------:|:-----------------------------------------------------------------------------------------------------------|
| `XXXXXX`<sup>1</sup> | Cutscene stored in file path `data_m\c1_txt\c1_fhll\txt_XXXXXX.txt`<sup>1</sup> relative to `Cultures.exe` |

↑ <sup>1</sup>Where `XXXXXX` are any six decimal digits.

### `Type`

| Value | Value meaning                                                     |
|:-----:|:------------------------------------------------------------------|
|  `0`  | Mission is activated from start. All goals must be completed.     |
|  `1`  | Mission is activated from start. One goal must be completed.      |
|  `2`  | Mission is activated from start. None of goals must be completed. |
|  `3`  | Mission is deactivated from start.                                |
|  `4`  | Mission is activated from start. Half of goals must be completed. |
|  `5`  | Mission is completed                                              |

### `AddGoal`

| Goal type | Value type                                          | Arguments                                                 | Arguments meaning                                                        |
|:---------:|-----------------------------------------------------|-----------------------------------------------------------|:-------------------------------------------------------------------------|
|    `0`    | integer \| integer \| integer \| integer \| integer | acting player \| target player \| good type \| good count | Trade with player.                                                       |
|    `1`    | integer                                             | player                                                    | Check is player killed.                                                  |
|    `2`    | integer \| integer \| integer                       | player \| good type \| good count                         | Collect goods.                                                           |
|    `3`    | integer \| integer \| integer \| integer            | x \| y \| good type \| good count                         | Collect goods in house.                                                  |
|    `4`    | integer \| integer \| integer \| integer \| string  | player \| x \| y \| radius \| house type                  | Build specific house in area.                                            |
|    `5`    | integer \| integer \| integer \| integer            | player \| x \| y \| radius                                | Build any house in area.                                                 |
|    `6`    | integer \| string \| integer                        | player \| house type \| number of houses                  | Build multiple instances of specific house in area.                      |
|    `7`    | string                                              | mission name                                              | Check is another mission completed.                                      |
|    `8`    | integer \| integer                                  | player \| population                                      | Reach population.                                                        |
|    `9`    | integer                                             | player                                                    | Build any house by player.                                               |
|   `10`    | integer \| integer                                  | acting player \| target player                            | Find player by player.                                                   |
|   `11`    | integer \| integer                                  | acting player \| target player                            | Check is diplomacy set to friendly.                                      |
|   `12`    | integer \| integer                                  | acting player \| target player                            | Check is diplomacy set to enemy.                                         |
|   `13`    | integer \| integer                                  | acting player \| target player                            | Start trading with player.                                               |
|   `14`    | integer \| integer                                  | player \| job type                                        | Unlock job.                                                              |
|   `15`    | integer \| integer \| integer \| integer            | player \| x \| y \| radius                                | Place any construction site in area.                                     |
|   `16`    | integer \| integer \| integer                       | acting player \| target player \| number of houses        | Destroy number of houses.                                                |
|   `17`    | integer \| integer \| integer                       | acting player \| target player \| number of units         | Kill number of units.                                                    |
|   `18`    | integer \| integer                                  | player \| number of units                                 | Assign houses to given number of units.                                  |
|   `19`    | integer \| integer \| integer \| integer            | player \| x \| y \| radius                                | Check is area explored by player.                                        |
|   `20`    | integer \| integer \| integer \| integer            | player \| x \| y \| radius                                | Place signpost in area.                                                  |
|   `21`    | integer \| integer                                  | player \| number of soldiers                              | Train total number of soldiers.                                          |
|   `22`    | integer \| integer                                  | duration (in seconds)                                     | Wait time.                                                               |
|   `23`    | integer \| integer                                  | x \| y                                                    | Let creature initialized on given position die or be killed.<sup>2</sup> |
|   `24`    | -                                                   | -                                                         | Obtain any hireling creature<sup>3</sup> by player zero.<sup>2</sup>     |

### `AddResult`

| Result type | Value type                                          | Arguments                                       | Arguments meaning                                                           |
|:-----------:|-----------------------------------------------------|-------------------------------------------------|:----------------------------------------------------------------------------|
|     `0`     | -                                                   | -                                               | Fail mission.                                                               |
|     `1`     | integer \| integer                                  | campaign mission ID to unlock \| campaign ID    | Win mission.                                                                |
|     `2`     | -                                                   | -                                               | Exit mission and play cutscene. (*Discovery of Vinland*)                    |
|     `3`     | integer \| integer                                  | acting player \| target player                  | Set diplomacy to friendly.                                                  |
|     `4`     | integer \| integer                                  | acting player \| target player                  | Set diplomacy to neutral.                                                   |
|     `5`     | integer \| integer                                  | acting player \| target player                  | Set diplomacy to enemy.                                                     |
|     `6`     | integer \| integer                                  | player \| house definition index<sup>4</sup>    | Unlock house.                                                               |
|     `7`     | integer \| integer                                  | player \| job type<sup>5</sup>                  | Unlock job.                                                                 |
|     `8`     | string                                              | mission name                                    | Disable mission.                                                            |
|     `9`     | string \| integer                                   | mission name \| mission type                    | Enable mission and set its type.                                            |
|    `10`     | integer \| integer \| integer                       | x \| y \| radius                                | Explore area.                                                               |
|    `11`     | integer \| integer \| integer \| integer            | always `1` \| player \| condition \| activity   | Change activity state of AI condition.                                      |
|    `12`     | integer \| integer \| integer \| integer \| integer | x \| y \| player \| job type \| number of units | Spawn units.<sup>2</sup>                                                    |
|    `13`     | -                                                   | -                                               | Exit mission and play cutscene.<sup>2</sup> (*The Revenge of the Rain God*) |

↑ <sup>2</sup> Exclusive for *Cultures: The Revenge of the Rain God*  
↑ <sup>3</sup> Hireling creature is defined by job type equal to `45`, `46` or `47`.  
↑ <sup>4</sup> House definition index is the number of relevant `House`
section in `data_v\ve_graphics\houses\houses.cif` file fould after extracting
`data_l\data_v.lib` library. Indices are counted from zero.  
↑ <sup>5</sup> Limited to job types ranging from `0` to `48`.

### Modifiable `data_v` values

Multiple values of specific types for `Mission` section can be found in
`*.cif` files after extracting `data_l\data_v.lib` library to game's main
directory. For more details check documentation specific for [`*.lib`](../formats/library.md),
[`*.cif`](../formats/cultures_initialization.md) and [`*.ini`](../formats/initialization.md) files.

| Type       | Path                                                       | Section        | Key         |
|:-----------|:-----------------------------------------------------------|:---------------|:------------|
| job type   | `data_v\ve_graphics\creatures\z_creature_descriptions.cif` | `CreatureType` | `MasterJob` |
| house type | `data_v\ve_graphics\houses\houses.cif`                     | `House`        | `Name`      |
| good type  | `data_v\ve_graphics\goods\goods.cif`                       | `Good`         | `Type`      |