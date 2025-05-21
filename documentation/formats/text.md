[← index](../index.md)

## Text file `(*.txt)`

### Introduction

[Text files](https://en.wikipedia.org/wiki/Text_file) are a common
type of file, which is not exclusive to *Cultures* video games. However, there
are exclusive text-formatting phases used by the game to correctly display the
content of `.txt` file.

### Syntax

Text files present in *Cultures* correspond to in-game briefings, which are
commonly known as yellowed papers usually containing a part of story relevant
to the gameplay. It is possible to include in such texts custom images, fonts
and other parameters typical of text formatting tools. For this purpose, text
files use keyword-value pairs denoted as `<keyword:value>`. All possible
keywords are available in the [briefings keywords](../briefings/text.md)
documentation. There is no special syntax for values, as they are just text.
However, it is common for integers to be separated by commas. Additionally,
new lines can be denoted as `\n`.

### Encoding

When writing non-[ASCII](https://en.wikipedia.org/wiki/ASCII) characters in
`*.txt` files it is important to use [Windows-1252](https://en.wikipedia.org/wiki/Windows-1252)
encoding, which is not compatible with widely used [Unicode](https://en.wikipedia.org/wiki/Unicode)
or [UTF-8](https://en.wikipedia.org/wiki/UTF-8). Therefore, it is recommended
to use [Notepad++](https://notepad-plus-plus.org/downloads/) and manually
change encoding in option `Encoding > Character sets > Western European > Windows-1252`.
This functionality is usually not accessible in the default preinstalled text
editors on commonly used operating systems.

Note that the exact encoding might differ for specific language editions
other than the most popular English and German versions of the game. However,
it is common for *Cultures* to use constant number of bytes per character
which excludes [Unicode](https://en.wikipedia.org/wiki/Unicode) and [UTF-8](https://en.wikipedia.org/wiki/UTF-8)
from being widely used in translations.