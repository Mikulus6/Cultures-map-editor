[← index](../index.md)

## `[AI]`
| Key                                        | Key meaning                                                                          | Arguments                                                                                                                                      |
|:-------------------------------------------|:-------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------|
| `AI_MainTask_Defend`                       | If condition is active, player will defend given area with given number of soldiers. | player \| x \| y \| radius \| soldiers minimum \| soldiers maximum \| condition \| priority **// unsure**                                      |
| `AI_MainTask_Attack`                       | If condition is active, player will attack given area with given number of soldiers. | player \| x \| y \| radius \| soldiers minimum \| soldiers maximum \| condition \| priority **// unsure**                                      |
| `AI_MainTask_BuildHouse`                   | If condition is active, player builds given building on given position.              | player \| house type \| x \| y \| priority \| condition   **// unsure**                                                                        |
| `AI_MainTask_ChangeDiplomacy`              | If condition is active, player changes diplomacy status towards target player.       | player \| diplomacy state \| target player \| priority \| condition  **// unsure**                                                             |
| `AI_MainTask_CreateCreatures`              | If condition is matching, player creates given creatures on given position.          | player \| job type \| x \| y \| quantity \| [?] \| condition \| matching condition state                                                       |
| `AI_MainTask_SelfDestroyPlayer`            | If condition is active, player becomes dead.                                         | player \| condition                                                                                                                            |
| `AI_MainTask_ClearTributes`                | If condition is active, player clears its tributes.                                  | player \| condition                                                                                                                            |
| `AI_MainTask_BuildMilestone`               | If condition is active, player builds signpost on given position                     | player \| x \| y \| priority[?] \| condition **// unsure**                                                                                     |
| `AI_SetCondition_True`                     | Condition is activated without any requirements.                                     | player \| condition                                                                                                                            |
| `AI_SetCondition_OnTime`                   | Condition is activated after given time.                                             | player \| condition \| duration (minutes)                                                                                                      |
| `AI_SetCondition_OnConditions`             | Condition is activated based on activity of other conditions.                        | player \| condition \| is always active \| quantifier type \| * referenced conditions                                                          |
| `AI_SetCondition_OnConditionChangeDelayed` | Condition is activated after given time since another condition was activated.       | player \| condition \| is always active \| observed condition \| target activity state of observed condition \| duration (seconds)             |
| `AI_SetCondition_OnDiplomacyChange`        | Condition is activated when acting player changes diplomacy status to target player. | player \| condition \| is always active \| acting player \| target player \| diplomacy state                                                   |
| `AI_SetCondition_OnCreatureInRange`        | Condition is activated if acting player has creature in given area.                  | player \| condition \| is always active \| x \| y \| radius \| acting player \| is hostility required \| are units soldiers                    |
| `AI_SetCondition_OnHouseInRange`           | Condition is activated when acting player places building in given area.             | player \| condition \| is always active \| x \| y \| radius \| acting player \| is hostility required \| building type \| is building finished |
| `AI_SetCondition_OnPlayerSeen`             | Condition is activated when acting player discovers target player.                   | player \| condition \| is always active \| acting player \| target player                                                                      |
| `AI_SetCondition_OnPlayerDead`             | Condition is activated when target player is dead.                                   | player \| condition \| target player                                                                                                           |
| `AI_SetCondition_OnNumberOfSoldiers`       | Condition is activated when target player has at least given number of soldiers.     | player \| condition \| is always active \| number of soldiers \| target player                                                                 |
| `AI_SetCondition_OnExternal`               | Condition has initial value which can be changed by missions.                        | player \| condition \| is active on start                                                                                                      |
| `AI_AddTribute`                            | Specified tribute is available to change diplomacy state.<sup>1</sup>                | player \| tribute type \| good type \| good count \| good type \| good count ...                                                               |
| `AI_SetTributeHireling`                    | Creates given hireling creatures when specified tribute is being paid.               | player \| tribute type<sup>2</sup> \| job type \| quantity \| job type \| quantity ...                                                         |
| `AI_UnitLimit`                             | Player will not create more babies after reaching this limit.                        | player \| amount                                                                                                                               |
| `AI_SoldiersDefaultPosition`               | Player will gather their armies in this area and defend it by default.               | player \| x \| y \| range                                                                                                                      |
| `AI_Disable`                               | Player ignores all tasks and do not develop.                                         | player                                                                                                                                         |

↑ <sup>1</sup> One can declare multiple tributes for repetitve diplomacy status changes.  
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

### Tribute type

| Value | Value meaning                                                  |
|:------|:---------------------------------------------------------------|
| `1`   | Changes diplomacy status to friend.                            |
| `2`   | Changes diplomacy status to neutral.                           |
| `3`   | Followed by `AI_SetTributeHireling` spawns hireling creatures. |