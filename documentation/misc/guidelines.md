[← index](../index.md)

## Publishing guidelines

### Introduction

The following guidelines are meant to provide rules that unify the way maps
are published after being created using the editor and to prevent unwanted
chaos that could arise from the lack of such guidelines. They are not enforced
in any way, yet it is recommended to follow them to make it easier for players
to install maps in a unified manner. Note that these rules might not apply in
every community, or that a community might have additional rules besides what
is provided here.

### Guidelines

#### Structural universality

Every map should be shared or published in the form of an archive or a
directory. A map shared as an archive should contain, within itself, an
archived directory with the map. The content of the directory with the map,
upon being copied or moved to the `data_m` directory (with replacement of
already existing files), should be the only process that makes up the entire
installation procedure of a given map. We condemn the usage of small executable
files that automate this process, popularized by previous generations of
map-makers, due to digital safety concerns and potential vulnerabilities.

#### Independency

Every map must be independent of other maps. When installing a map, it is
prudent to assume that the player does not have any other map installed. This
condition can be checked by temporarily deleting the entire content of the
`data_m` directory and the `data_l\data_m.lib` archive, then inserting the
finished map into an empty `data_m` directory and checking in the game whether
it works correctly. This condition does not include dependency on any data
provided by the game files outside the mentioned archive and directory, as
such files and directories are considered an immanent attribute of a given
game version. The map may use preexisting files (especially in the `c1_txt`
subdirectory), but despite them being present in the original game, they shall
also be provided as part of the map being installed, as if the player did not
have them in their copy of the game, because they are part of the `data_m`
directory.

#### Non-interferability

Every map must not interfere with the state of any other map. In other words,
it should be possible to have any two maps correctly installed at the same
time. The easiest way to enforce this condition is to not modify files that
already exist during the map development process. Instead, create a new file
and modify its content rather than using an existing one. To enforce this
condition with other maps made in the editor that are not present by default
in the game, check existing maps online within the scope of possibilities
before publishing your own map. Consequently, due to this rule, a map should
not contain any [`*.ini`](../formats/initialization.md) files. They should be
replaced with appropriate [`*.cif`](../formats/cultures_initialization.md)
files.

#### Version compatibility

Every map, upon being shared or published, should clearly mention the version
of the game for which it is intended to be played on. If changes outside the
`data_m` directory within the game files are required for a map to work
correctly, such changes are considered a modification of the game rather than
part of the map, making it incompatible with a non-modified version of the
game. In such a scenario, it should be mentioned on which game version a
modification must be installed first. Otherwise, a separate standalone
modification must be provided together with the map or have been previously
published.

#### Beatability

Every map should be technically beatable, unless specified otherwise for the
player in an accessible briefing or mentioned in an additional description on
the website where the map is shared or published. It is the duty of the
creator or creators of a given map to guarantee its beatability. The creator
or creators may agree with someone else to be a tester or testers of the map.
In such a situation, the responsibility for map beatability is passed onto the
mentioned tester or testers. This condition is an ethical condition,
not a technical one.

### Where to publish

There is no central website that has absolute authority to publish maps. The
two most popular sites for this purpose are currently the Polish
[CulturesNation](https://culturesnation.pl/) and the German
[Wikinger-Tommy](https://www.wikinger-tommy.de/). If you want to publish a map
that is playable only in one of the mentioned languages, publish it on the
respective website. Otherwise, it is up to you where to publish your map.
Note that each website might have its own additional guidelines for map
publication.