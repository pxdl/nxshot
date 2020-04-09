# nxshot
Automatically organize and timestamp your Nintendo Switch captures
![image](https://user-images.githubusercontent.com/17756301/33006063-0c36d2ce-cdb0-11e7-8875-1044eab6527a.png)

# !!! This Project has been deprecated in favor of [Switcheroo](https://github.com/Tyler-A/Switcheroo) / [Switcheroo Lite](https://github.com/dmynerd78/switcheroo-lite) !!!

## Requirements
This package requires pycryptodome and BeautifulSoup4.
You can install them by running
``pip install -r requirements.txt``

(Optional) Key at offset 0x71000704D0 from the capsrv NSO loaded up in IDA as ``key.txt`` on the same folder as nxshot for automatic updating. Hash: ``24e0dc62a15c11d38b622162ea2b4383``

## Usage

``nxshot.py [-h] [-d] FILEPATH``

positional arguments:

    FILEPATH                         "Nintendo/Album" folder from your SD card.

optional arguments:

    -h, --help                       show this help message and exit
    -d, --download-nswdb             Download IDs from nswdb.com instead of switchbrew.org
                                     NOTE: Regions may not match SwitchBrew

![image](https://user-images.githubusercontent.com/17756301/33006113-3f204800-cdb0-11e7-99f4-94790c01916d.png)

Organized and tagged files are copied to ``../Nintendo/Album/Organized`` in a folder with the game's name.

If some of your screenshots end up being copied to ``../Nintendo/Album/Organized/Unknown``, please open an issue with the game id from the screenshot filename so that I can update the gameid list.

## Current gameid list

To see what games are currently automatically recognized, take a look at the [gameids.json](gameids.json) file.

The list is automatically updated from [SwitchBrew](http://switchbrew.org/index.php?title=Title_list/Games) by default. [nswdb](http://nswdb.com/) can be used with the ``-d`` flag.

## Help

If you have any questions, feel free to send me a tweet [**@Some1CP**](https://twitter.com/Some1CP).
