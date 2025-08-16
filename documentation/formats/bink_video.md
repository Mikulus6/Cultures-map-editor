[← index](../index.md)

## Bink video (`*.bik`)

### Introduction

Bink video is a common file format used to store information about video
cutscenes. More specific documentation can be found in the [Bink Video Wikipedia article](https://en.wikipedia.org/wiki/Bink_Video).
This file format can be opened and modified with [RAD Video Tools](https://www.radgametools.com/bnkdown.htm).
In *Cultures* this file format is used to store videos for the intro and outro
cutscenes.

Note that, when downloading [RAD Video Tools](https://www.radgametools.com/bnkdown.htm)
from the official website, a password is required to extract the downloaded
archive. Because of this, it might be necessary to install [WinRAR](https://www.win-rar.com/start.html)
first and use it to type in the password.

### Modifying

In order to replace a video cutscene in the game with a different one, using [RAD Video Tools](https://www.radgametools.com/bnkdown.htm),
one must export a given video to a common file format first, such as
`*.avi` or `*.mp4`. Next, by using the aforementioned application, select the
chosen file in the explorer and use the option `RAD Video Tools > Bink it!`.
In the settings, choose `Compression settings > File format > Bink 1` and use
the option `Bink` to render a new video in the `*.bik` file format. If audio
is absent when the video is playing in the game, go back to the `Bink Compressor`
window and add `100` to the value present in `Compress audio > Compress level`.
This operation should, by default, result in this value changing from `4` to
`104`. After rendering the video again with the `Bink` option, sound should be
present when the video cutscene plays in the game.