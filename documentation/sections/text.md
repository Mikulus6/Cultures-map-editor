[← index](../index.md)

## `[text]`

| Key  | Value type        | Value meaning                                |
|:-----|:------------------|:---------------------------------------------|
| `sn` | integer \| string | string ID \| language-dependent string value |
| `s`  | string            | language-dependent string value              |

This `[text]` section should be stored in separated file and linked to main
file via `TextFile` entry in `[Control]` section.

Phase `{MISC}` in strings might have special meaning for in-game display.

String in `s` entry has hidden ID equal to the smallest available numeric value
greater than last used numeric value in `sn` entry. Therefore, first entry in
this section should start with `sn 0`.