[← index](../index.md)

## `[AI]`

| Key                                        | Value type                                                                                                 | Arguments                                                                                                                                      | Arguments meaning                                                                    |
|:-------------------------------------------|:-----------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------|
| `AI_MainTask_Defend`                       | integer \| integer \| integer \| integer \| integer \| integer \| integer \| integer                       | player \| x \| y \| radius \| soldiers minimum \| soldiers maximum \| priority \| condition                                                    | If condition is active, player will defend given area with given number of soldiers. |
| `AI_MainTask_Attack`                       | integer \| integer \| integer \| integer \| integer \| integer \| integer \| integer                       | player \| x \| y \| radius \| soldiers minimum \| soldiers maximum \| priority \| condition                                                    | If condition is active, player will attack given area with given number of soldiers. |
| `AI_MainTask_BuildHouse`                   | integer \| string \| integer \| integer \| integer \| integer                                              | player \| house type \| x \| y \| priority \| condition                                                                                        | If condition is active, player builds given building on given position.              |
| `AI_MainTask_ChangeDiplomacy`              | integer \| integer \| integer \| integer \| integer                                                        | player \| diplomacy status \| target player \| priority \| condition                                                                           | If condition is active, player changes diplomacy status towards target player.       |
| `AI_MainTask_CreateCreatures`              | integer \| integer \| integer \| integer \| integer \| integer \| integer \| integer                       | player \| job type \| x \| y \| quantity \| priority \| condition \| matching condition state                                                  | If condition is matching, player creates given creatures on given position.          |
| `AI_MainTask_SelfDestroyPlayer`            | integer \| integer                                                                                         | player \| condition                                                                                                                            | If condition is active, player becomes dead.                                         |
| `AI_MainTask_ClearTributes`                | integer \| integer                                                                                         | player \| condition                                                                                                                            | If condition is active, player clears its tributes.                                  |
| `AI_MainTask_BuildMilestone`               | integer \| integer \| integer \| integer \| integer                                                        | player \| x \| y \| priority \| condition                                                                                                      | If condition is active, player builds signpost on given position                     |
| `AI_SetCondition_True`                     | integer \| integer                                                                                         | player \| condition                                                                                                                            | Condition is activated without any requirements.                                     |
| `AI_SetCondition_OnTime`                   | integer \| integer \| integer                                                                              | player \| condition \| duration (minutes)                                                                                                      | Condition is activated after given time.                                             |
| `AI_SetCondition_OnConditions`             | integer \| integer \| integer \| integer \| *integer                                                       | player \| condition \| is always active \| quantifier type \| * referenced conditions                                                          | Condition is activated based on activity of other conditions.                        |
| `AI_SetCondition_OnConditionChangeDelayed` | integer \| integer \| integer \| integer \| integer \| integer                                             | player \| condition \| is always active \| observed condition \| target activity state of observed condition \| duration (seconds)             | Condition is activated after given time since another condition was activated.       |
| `AI_SetCondition_OnDiplomacyChange`        | integer \| integer \| integer \| integer \| integer \| integer                                             | player \| condition \| is always active \| acting player \| target player \| diplomacy status                                                  | Condition is activated when acting player changes diplomacy status to target player. |
| `AI_SetCondition_OnCreatureInRange`        | integer \| integer \| integer \| integer \| integer \| integer \| integer \| integer \| integer            | player \| condition \| is always active \| x \| y \| radius \| acting player \| is hostility required \| are units soldiers                    | Condition is activated if acting player has creature in given area.                  |
| `AI_SetCondition_OnHouseInRange`           | integer \| integer \| integer \| integer \| integer \| integer \| integer \| integer \| integer \| integer | player \| condition \| is always active \| x \| y \| radius \| acting player \| is hostility required \| building type \| is building finished | Condition is activated when acting player places building in given area.             |
| `AI_SetCondition_OnPlayerSeen`             | integer \| integer \| integer \| integer \| integer                                                        | player \| condition \| is always active \| acting player \| target player                                                                      | Condition is activated when acting player discovers target player.                   |
| `AI_SetCondition_OnPlayerDead`             | integer \| integer \| integer                                                                              | player \| condition \| target player                                                                                                           | Condition is activated when target player is dead.                                   |
| `AI_SetCondition_OnNumberOfSoldiers`       | integer \| integer \| integer \| integer \| integer                                                        | player \| condition \| is always active \| number of soldiers \| target player                                                                 | Condition is activated when target player has at least given number of soldiers.     |
| `AI_SetCondition_OnExternal`               | integer \| integer \| integer                                                                              | player \| condition \| is active on start                                                                                                      | Condition has initial value which can be changed by missions.                        |
| `AI_AddTribute`                            | integer \| integer \| integer \| integer \| integer \| integer ...                                         | player \| tribute type \| good type \| good count \| good type \| good count ...                                                               | Specified tribute is available to change diplomacy state.<sup>1</sup>                |
| `AI_SetTributeHireling`                    | integer \| integer \| integer \| integer \| integer \| integer ...                                         | player \| tribute type<sup>2</sup> \| job type \| quantity \| job type \| quantity ...                                                         | Creates given hireling creatures when specified tribute is being paid.               |
| `AI_UnitLimit`                             | integer \| integer                                                                                         | player \| amount                                                                                                                               | Player will not create more babies after reaching this limit.                        |
| `AI_SoldiersDefaultPosition`               | integer \| integer \| integer \| integer                                                                   | player \| x \| y \| range                                                                                                                      | Player will gather their armies in this area and defend it by default.               |
| `AI_Disable`                               | integer                                                                                                    | player                                                                                                                                         | Player ignores all tasks and do not develop.                                         |

↑ <sup>1</sup> One can declare multiple tributes for repetitive diplomacy status changes.  
↑ <sup>2</sup> Tribute type for `AI_SetTributeHireling` key has value always equal to `3`.  

### Modifiable `data_v` values

Multiple values of specific types for `AI` section can be found in
`*.cif` files after extracting `data_l\data_v.lib` library to game's main
directory. For more details check documentation specific for [`*.lib`](../formats/library.md),
[`*.cif`](../formats/cultures_initialization.md) and [`*.ini`](../formats/initialization.md) files.

| Type       | Path                                                       | Section        | Key         |
|:-----------|:-----------------------------------------------------------|:---------------|:------------|
| job type   | `data_v\ve_graphics\creatures\z_creature_descriptions.cif` | `CreatureType` | `MasterJob` |
| house type | `data_v\ve_graphics\houses\houses.cif`                     | `House`        | `Name`      |
| good type  | `data_v\ve_graphics\goods\goods.cif`                       | `Good`         | `Type`      |

### Diplomacy status
| Value | Value meaning |
|:------|:--------------|
| `0`   | enemy         |
| `1`   | neutral       |
| `2`   | friend        |

### Quantifier type
| Value | Value meaning                                          |
|:------|:-------------------------------------------------------|
| `1`   | All conditions must be active.                         |
| `2`   | At least one condition must be active.                 |
| `3`   | The only condition must be inactive.                   |
| `4`   | Exactly one of the only two conditions must be active. |

### Tribute type
| Value | Value meaning                                                  |
|:------|:---------------------------------------------------------------|
| `1`   | Changes diplomacy status to friend.                            |
| `2`   | Changes diplomacy status to neutral.                           |
| `3`   | Followed by `AI_SetTributeHireling` spawns hireling creatures. |