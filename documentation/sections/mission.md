[← index](../index.md)

## `[Mission]`
| Key           | Arguments                                        | Value meaning                                                  |
|:--------------|:-------------------------------------------------|:---------------------------------------------------------------|
| `StartText`   | cutscene id                                      | cutscene played when mission becomes active                    |
| `StartTime`   | seconds                                          | duration from start before mission is checked (in seconds)     |
| `Text`        | cutscene id                                      | cutscene played when mission becomes complete                  |
| `Name`        | string                                           | mission name used as a textual ID in other missions            |
| `Type`        | mission type                                     | mission initial activity state and completion quantifier       |
| `AddGoal`     | goal type \| * miscellaneous goal parameters     | see [AddGoal](#addgoal) chapter                                |
| `AddResult`   | result type \| * miscellaneous result parameters | see [AddResult](#addresult) chapter                            |
| `SetGoalText` | `AddGoal` index \| string id                     | goal text will be completed if this specific goal is completed |

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
| `10`  | [?]                                                               |

### `AddGoal`

| Goal type | Type meaning                                        | Arguments                                                 |
|:---------:|:----------------------------------------------------|-----------------------------------------------------------|
|    `0`    | Trade with player.                                  | acting player \| target player \| good type \| good count |
|    `1`    | Check is player killed.                             | player                                                    |
|    `2`    | Collect goods.                                      | player \| good type \| good count                         |
|    `3`    | Collect goods in house.                             | x \| y \| good type \| good count                         |
|    `4`    | Build specific house in area.                       | player \| x \| y \| radius \| house type                  |
|    `5`    | Build any house in area.                            | player \| x \| y \| radius                                |
|    `6`    | Build multiple instances of specific house in area. | player \| house type \| number of houses                  |
|    `7`    | Check is another mission completed.                 | mission name                                              |
|    `8`    | Reach population.                                   | player \| population                                      |
|    `9`    | Build any house by player.                          | player                                                    |
|   `10`    | Find player by player.                              | acting player \| target player                            |
|   `11`    | Check is diplomacy set to friendly.                 | acting player \| target player                            |
|   `12`    | Check is diplomacy set to enemy.                    | acting player \| target player                            |
|   `13`    | Start trading with player.                          | acting player \| target player                            |
|   `14`    | Unlock job.                                         | player \| job type                                        |
|   `15`    | Place any construction site in area.                | player \| x \| y \| radius                                |
|   `16`    | Destroy number of houses.                           | acting player \| target player \| number of houses        |
|   `17`    | Kill number of units.                               | acting player \| target player \| number of units         |
|   `18`    | Assign houses to given number of units.             | player \| number of units                                 |
|   `19`    | Check is area explored by player.                   | player \| x \| y \| radius                                |
|   `20`    | Place signpost in area.                             | player \| x \| y \| radius                                |
|   `21`    | Train total number of soldiers.                     | player \| number of soldiers                              |
|   `22`    | Wait time.                                          | duration (in seconds)                                     |
|   `23`    | [?]<sup>2</sup>                                     |                                                           |
|   `24`    | [?]<sup>2</sup>                                     | -                                                         |

### `AddResult`

| Result type | Type meaning                                                               | Arguments                                                        |
|:-----------:|:---------------------------------------------------------------------------|------------------------------------------------------------------|
|     `0`     | Fail mission.                                                              | -                                                                |
|     `1`     | Win mission.                                                               | campaign mission id to unlock \| campaign id                     |
|     `2`     | Win mission and play cutscene. (*Discovery of Vinland*)                    | -                                                                |
|     `3`     | Set diplomacy to friendly.                                                 | acting player \| target player                                   |
|     `4`     | Set diplomacy to neutral.                                                  | acting player \| target player                                   |
|     `5`     | Set diplomacy to enemy.                                                    | acting player \| target player                                   |
|     `6`     | Unlock house in tech tree.                                                 | player \| house type<sup>3</sup>                                 |
|     `7`     | Unlock job in school.                                                      | player \| job type<sup>4</sup>                                   |
|     `8`     | Disable mission.                                                           | mission name                                                     |
|     `9`     | Enable mission and set its type.                                           | mission name \| mission type                                     |
|    `10`     | Explore area.                                                              | x \| y \| radius                                                 |
|    `11`     | Change active AI condition.                                                | must be `1` \| player \| condition id \| enable(1) or disable(0) |
|    `12`     | Spawn units.<sup>2</sup>                                                   | x \| y \| player \| job type \| number of units                  |
|    `13`     | Win mission and play cutscene.<sup>2</sup> (*The Revenge of the Rain God*) | -                                                                |

↑ <sup>2</sup> Exclusive for *Cultures: The Revenge of the Rain God*

↑ <sup>3</sup> Only houses ids are supported, in order of appearance in the `houses.cif` file.

↑ <sup>4</sup> Limited to job types 0-48.