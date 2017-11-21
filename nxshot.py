import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime
from shutil import copy


# Load game ids and their names from external file
try:
    with open('gameids.json', 'r') as idfile:
            idname = json.load(idfile)
except FileNotFoundError:
    print('Game ID list (gameids.json) not found! Exitting...')
    sys.exit()
except json.decoder.JSONDecodeError:
    print('Invalid JSON format! Exitting...')
    sys.exit()

# Argument parser
parser = argparse.ArgumentParser(
    description='Automatically organize and timestamp\
                 your Nintendo Switch captures.')

parser.add_argument(
    'filepath',
    metavar='FILEPATH',
    type=Path,
    help='"Nintendo/Album" folder from your SD card.')

# If there are arguments, parse them. If not, exit
args = parser.parse_args()


def checkID(gameid, idname):
    if gameid in idname:
        return idname[gameid]
    else:
        return 'Unknown'


def checkFolders(filelist):
    current = 0
    length = len(filelist)
    #print(filelist)
    for mediapath in filelist:
        year = mediapath.stem[0:4]
        month = mediapath.stem[4:6]
        day = mediapath.stem[6:8]
        hour = mediapath.stem[8:10]
        minute = mediapath.stem[10:12]
        second = mediapath.stem[12:14]
        gameid = mediapath.stem[17:]

        try:
            time = datetime(
                            int(year),
                            int(month),
                            int(day),
                            hour=int(hour),
                            minute=int(minute),
                            second=int(second))
            pass
        except ValueError:
            print(
                'Invalid filename for media {}: {}'.format(
                                                        current,
                                                        str(mediapath.stem)
                                                        )
                )
            continue

        posixtimestamp = time.timestamp()

        outputfolder = args.filepath.joinpath('Organized', checkID(gameid,idname))

        outputfolder.mkdir(parents=True, exist_ok=True)

        newfile = copy(str(mediapath), str(outputfolder))

        os.utime(newfile, (posixtimestamp, posixtimestamp))

        current += 1

        print('Organized {} of {} files.'.format(current, length))


albumfolder = args.filepath

screenshotlist = sorted(
        Path(albumfolder).glob(
            '[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]/*.jpg'
            )
        )

videolist = sorted(
        Path(albumfolder).glob(
            '[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]/*.mp4'
            )
        )

if len(screenshotlist) != 0:
    print('Organizing screenshots...')
    checkFolders(screenshotlist)
else:
    print('No screenshots found!')

if len(videolist) != 0:  
    print('\nOrganizing videos...')
    checkFolders(videolist)
else:
    print('\nNo videos found!')

print('Done!')
