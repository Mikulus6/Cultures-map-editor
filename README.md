# Cultures Map Editor

## Introduction

Following application is meant to be a tool for map-making process in video
games  [*Cultures: Discovery of Vinland*](https://www.gog.com/en/game/cultures_12)
and [*Cultures: The Revenge of the Rain God*](https://www.mobygames.com/game/6100/cultures-die-rache-des-regengottes/).
It makes it possible to freely view and edit `*.map` files from 
mentioned games. Available functionalities are implemented in a way which
mimic editors present in other games from *Cultures* series.

## Installation

After downloading necessary files from [*releases section*](https://github.com/Mikulus6/Cultures-map-editor/releases)
make sure to put them in game's main directory, so that the downloaded
executable file and `Cultures.exe` file are in the same location.
Alternatively you can copy `data_l` folder from game files and paste it to
directory of newly downloaded application.

Note that when opening the program for the first time it will try to generate
`cache.bin` file which can take significant time to load. If you  want to skip
this process you might be able to find this file online, however due to
copyright restrictions we do not provide access to such file here.

Project was tested on Python 3.13 with all used third party libraries being up
to date at the moment of publication.

## Credits

This project is a fan-made tool made by [*CulturesNation*](https://culturesnation.pl/) community. It is not
affiliated with the official legacy of *Cultures* series. For official
developers' website, visit [*Funatics*](https://www.funatics.de/).

#### Contributors

[Mikulus](https://github.com/Mikulus6): Managed project and wrote most of Python code.  
[Basssiiie](https://github.com/Basssiiie): Decompiled important parts of game's engine via Ghidra.  
[Tyrannica](https://github.com/ARKAMENTOR): Helped with walk sectors' data visualisation.  

#### Referenced literature

bacter: "[*Unknown Encryption In Cultures Game*](https://web.archive.org/web/20210724220815/https://forum.xentax.com/viewtopic.php?t=3711)" (2010)  
[Siguza](https://github.com/Siguza): "[*Cultures 2 file formats*](https://web.archive.org/web/20210724220815/https://forum.xentax.com/viewtopic.php?t=3711)" (2013)  
[FinFET](https://github.com/FinFetChannel): "[*SimplePython3DEngine*](https://github.com/FinFetChannel/SimplePython3DEngine)" (2022)  
[Remik](https://github.com/kamil0495): "[*CEngine*](https://github.com/kamil0495/CEngine)" (2023)
