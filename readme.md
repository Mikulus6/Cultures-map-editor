# Cultures Map Editor

## Introduction

Following application is meant to be a tool for map-making process in video
games  [*Cultures: Discovery of Vinland*](https://www.gog.com/en/game/cultures_12)
and [*Cultures: The Revenge of the Rain God*](https://www.mobygames.com/game/6100/cultures-die-rache-des-regengottes/).
It makes it possible to freely view and modify `*.map` files from 
mentioned games. Available functionalities are implemented in a way which
mimics editors present in other games from *Cultures* series.

![example](assets/readme/example.png)

## Installation

After downloading necessary files from [*releases section*](https://github.com/Mikulus6/Cultures-map-editor/releases)
make sure to put them in game's main directory, so that the downloaded
executable file and `Cultures.exe` file are in the same location.
Alternatively you can copy `data_l` folder from game files and paste it to
directory of newly downloaded application.

Optionally, if you want to speed up the program startup you can extract
`data_l\data_v.lib` library to game's main directory. This way, during the
initialization process the application will be able to refer directly to
extracted files rather than searching for them in the relatively large
library.

Note that when opening the program for the first time it will try to generate
`cache.bin` file which can take significant time to load. If you  want to skip
this process you might be able to find this file online, however due to
copyright restrictions we do not provide access to such file here.  
Keep in mind that `cache.bin` files generated for *Cultures: Discovery of
Vinland* and *Cultures: The Revenge of the Rain God* will contain different
content and are not interchangeable.

Remember that the display of terrain and landscapes in the editor might not be
exactly the same as in the game. Always check important aesthetics by opening
`*.map` files via original game.

Project was tested on Python 3.13 with all used third party
libraries being up to date at the moment of publication.

## Credits

This project is a fan-made tool created by [*CulturesNation*](https://culturesnation.pl/)
community. It is not affiliated with the official legacy of *Cultures* series.
For official developers' website, visit [*Funatics*](https://www.funatics.de/).

### Contributors

[Mikulus](https://github.com/Mikulus6): Managed project and wrote most of Python code.  
[Basssiiie](https://github.com/Basssiiie): Decompiled important parts of game's engine via Ghidra.  
[Tyrannica](https://github.com/ARKAMENTOR): Helped with walk sectors' data visualisation.  
[Proszak](https://www.facebook.com/PigmentDesignStudio): Drew some of the graphics for user interface.

### Referenced literature

bacter: "[*Unknown Encryption In Cultures Game*](https://web.archive.org/web/20210724220815/https://forum.xentax.com/viewtopic.php?t=3711)" (2010)  
[Siguza](https://github.com/Siguza): "[*Cultures 2 file formats*](https://web.archive.org/web/20210724220815/https://forum.xentax.com/viewtopic.php?t=10705)" (2013)  
[FinFET](https://github.com/FinFetChannel): "[*SimplePython3DEngine*](https://github.com/FinFetChannel/SimplePython3DEngine)" (2022)  
[Remik](https://github.com/kamil0495): "[*CEngine*](https://github.com/kamil0495/CEngine)" (2023)

### License

This program and its source code are distributed under [*GNU General Public License 3.0*](https://www.gnu.org/licenses/gpl-3.0.txt),
which can be found in the [license.txt](license.txt) file. *Cultures* itself
is the property of [*Funatics Software*](https://www.funatics.de/) with all
rights reserved as stated in the game credits, and is not covered by the
aforementioned license.