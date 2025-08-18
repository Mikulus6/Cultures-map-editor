[← index](../index.md)

## Header file (`*.hpp`)

### Description

[Header file](https://en.wikipedia.org/wiki/Include_directive) is a common
file format used in [C++](https://en.wikipedia.org/wiki/C++). This file format
does not occur in the game files by default. To obtain `*.hpp` file one must
extract `data_l\data.lib` archive to the game's main directory as explained in
[`*.lib`](library.md) file format documentation. After that, by running
supplementary executable file present in newly extracted directory
`data\gui\texttableconverter.exe`, one can use the option `Convert` to create
a pair of files ([`*.tab`](text_table.md) and `*.hpp`). Such newly created
`Language.hpp` file is a remaining byproduct of the original development
process of *Cultures* and serves no known practical purpose in modding
procedures. This file can be opened using any text editor. It is recommended
to use [Notepad++](https://notepad-plus-plus.org/). This file format strongly
suggests that the *Cultures* game was originally written in
[C++](https://en.wikipedia.org/wiki/C++). For more details one can read
about header files in C++ on Microsoft Learn website ([*Header files (C++)*](https://learn.microsoft.com/en-us/cpp/cpp/header-files-cpp)).