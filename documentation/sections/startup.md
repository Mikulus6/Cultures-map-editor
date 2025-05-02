[← index](../index.md)

## `[StartUp]`
| Key                         | Value type                                                                | Arguments                                                                                                                   | Arguments meaning                                                                                                          |
|:----------------------------|:--------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------|
| `StartPos`                  | integer \| integer \| integer                                             | player \| x \| y                                                                                                            | Set starting camera positon for given player.                                                                              |
| `Tribe`                     | integer \| integer                                                        | player \| tribe type                                                                                                        | Set tribe type for given player.                                                                                           |
| `NameTribe`                 | integer \| integer                                                        | player \| string ID                                                                                                         | Set tribe name visible in diplomacy window for given player.                                                               |
| `NameChief`                 | integer \| integer                                                        | player \| string ID                                                                                                         | Set chief name visible in diplomacy window for given player.                                                               |
| `PureAIPlayer`              | integer                                                                   | player                                                                                                                      | Disable multiplayer selectability.                                                                                         |
| `NameDescription`           | integer \| integer                                                        | player \| string ID                                                                                                         | Set tribe description invisible in game for given player.                                                                  |
| `PlayerColor`               | integer \| integer                                                        | player \| color                                                                                                             | Set color for given player.                                                                                                |
| `SetCreature`               | integer \| integer \| integer \| integer \| integer                       | player \| job type \| x \| y \| quantity                                                                                    | Set ceatures in specified quantity for given player with given job on given position.                                      |
| `SetCreatureName`           | integer \| integer \| integer                                             | x \| y \| string ID                                                                                                         | Set name of creature on given starting positoin.                                                                           |
| `SetHouse`                  | integer \| string \| integer \| integer \| integer                        | player \| house type \| x \| y \| state                                                                                     | Set house for given player on given position with given state of completion.                                               |
| `AddHouseStock`             | integer \| integer \| string \| integer                                   | x \| y \| good type \| good count                                                                                           | Add goods to house on given position.                                                                                      |
| `SetCreatureHome`           | integer \| integer \| integer \| integer                                  | x (creature) \| y (creature) \| x<sup>1</sup> (home) \| y<sup>1</sup> (home)                                                | Assign creature to home by given positions.                                                                                |
| `SetCreatureWork`           | integer \| integer \| integer \| integer                                  | x (creature) \| y (creature) \| x<sup>1</sup> (work) \| y<sup>1</sup> (work)                                                | Assign creature to workplace by given positions.                                                                           |
| `SetCreaturePartner`        | integer \| integer \| integer \| integer                                  | x<sub>1</sub> \| y<sub>1</sub> \| x<sub>2</sub> \| y<sub>2</sub>                                                            | Marry two creatures on given positions.                                                                                    |
| `SetTradeOffer`             | integer \| integer \| integer \| integer \| integer \| integer \| integer | x \| y \| trade index \| good offered \| good offered count<sup>2</sup> \| good demanded \| good demanded count<sup>2</sup> | Create trade offer in house on given position with specified goods.                                                        |
| `SetMilestone`              | integer \| integer \| integer                                             | player \| x \| y                                                                                                            | Set signpost for given player on given coordinates.                                                                        |
| `ConnectMilestones`         | integer \| integer \| integer \| integer                                  | x<sub>1</sub> \| y<sub>1</sub> \| x<sub>2</sub> \| y<sub>2</sub>                                                            | Connect signposts on given positions.                                                                                      |
| `AllowHouse`                | integer \| string                                                         | player \| house type                                                                                                        | Unlock given house for given player.                                                                                       |
| `AllowJob`                  | integer \| integer                                                        | player \| job type                                                                                                          | Unlock given job for given player.                                                                                         |
| `ForbidHouse`               | integer \| string                                                         | player \| house type                                                                                                        | Block given house for given player.                                                                                        |
| `ForbidJob`                 | integer \| integer                                                        | player \| job type                                                                                                          | Block given job for given player.                                                                                          |
| `ExploreMap`                | integer \| integer \| integer \| integer                                  | player \| x \| y \| radius                                                                                                  | Explore area for given player.                                                                                             |
| `SetDiplomacy`              | integer \| integer \| integer                                             | acting player \| target player \| diplomacy status                                                                          | Set diplomacy status of acting player toward target player.                                                                |
| `Particles_AddFishes`       | float \| float \| int \| float \| float                                   | x \| y \| quantity \| linear speed factor \| exponential speed factor                                                       | Set fish particles in specified quantity on given position. Speed of each fish is determined by speed factors<sup>3</sup>. |
| `Particles_AddBirds`        | float \| float \| int \| float \| float                                   | x \| y \| quantity \| linear speed factor \| exponential speed factor                                                       | Set bird particles in specified quantity on given position. Speed of each fish is determined by speed factors<sup>3</sup>. |
| `MultiplayerTradingGoal`    | integer \| integer                                                        | good type \| good count                                                                                                     | Set production goal for multiplayer game.                                                                                  |
| `MultiplayerPopulationGoal` | integer                                                                   | population                                                                                                                  | Set population goal for multiplayer game.                                                                                  |
| `MultiplayerBriefings`      | integer \| integer                                                        | cutscene ID (start) \| cutscene ID (end)                                                                                    | Set briefings for beginning and ending of multiplayer map.                                                                 |

↑ <sup>1</sup>These coordinates must satisfy the following equation: `y mod 4 = 2·(x mod 2)`  
↑ <sup>2</sup>Goods quatities in trade offers cannot exceed the value `8`,
otherwise the trade offer will not work correctly.   
↑ <sup>3</sup>Speed of `n`-th particle-related animal is proportional to
formula `A·nᴮ`, where `A` is the linear speed factor and `B` is the
exponential speed factor.  

### Modifiable `data_v` values

Multiple values of specific types for `StartUp` section can be found in
`*.cif` files after extracting `data_l\data_v.lib` library to game's main
directory. For more details check documentation specific for [`*.lib`](../formats/library.md),
[`*.cif`](../formats/cultures_initialization.md) and [`*.ini`](../formats/initialization.md) files.

| Type       | Path                                                       | Section            | Key         |
|:-----------|:-----------------------------------------------------------|:-------------------|:------------|
| tribe type | `data_v\vg_logic\tribes\tribes.cif`                        | `TribeDescription` | `TribeId`   |
| job type   | `data_v\ve_graphics\creatures\z_creature_descriptions.cif` | `CreatureType`     | `MasterJob` |
| house type | `data_v\ve_graphics\houses\houses.cif`                     | `House`            | `Name`      |
| good type  | `data_v\ve_graphics\goods\goods.cif`                       | `Good`             | `Type`      |

### Color
| Value | Value meaning |            Color             |
|:------|:--------------|:----------------------------:|
| `0`   | blue          | ![0](../assets/colors/0.png) |
| `1`   | red           | ![1](../assets/colors/1.png) |
| `2`   | yellow        | ![2](../assets/colors/2.png) |
| `3`   | cyan          | ![3](../assets/colors/3.png) |
| `4`   | green         | ![4](../assets/colors/4.png) |
| `5`   | purple        | ![5](../assets/colors/5.png) |
| `6`   | grey          | ![6](../assets/colors/6.png) |
| `7`   | orange        | ![7](../assets/colors/7.png) |
| `8`   | brown         | ![8](../assets/colors/8.png) |
| `9`   | black         | ![9](../assets/colors/9.png) |

### State
| Value | Value meaning     |
|:------|:------------------|
| `0`   | construction site |
| `1`   | completed house   |

### Diplomacy status
| Value | Value meaning |
|:------|:--------------|
| `30`  | enemy         |
| `50`  | neutral       |
| `70`  | friend        |

### Cutscene ID
|        Value         | Value meaning                                                                                              |
|:--------------------:|:-----------------------------------------------------------------------------------------------------------|
| `XXXXXX`<sup>4</sup> | Cutscene stored in file path `data_m\c1_txt\c1_fhll\txt_XXXXXX.txt`<sup>4</sup> relative to `Cultures.exe` |
↑ <sup>4</sup>Where `XXXXXX` are any six decimal digits.


