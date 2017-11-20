import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
from shutil import copy

idname = {
          '8AEDFF741E2D23FBED39474178692DAF':'Super Mario Odyssey',
          '0FD58DE9E32A04CFA77A97DD70C63633':'Puyo Puyo Tetris Demo',
          '0585E865DFB68B5298F19360A730EDB3':'Puyo Puyo Tetris',
          'F1C11A22FAEE3B82F21B330E1B786A39':'The Legend of Zelda - Breath of the Wild',
          '57B4628D2267231D57E0FC1078C0596D':'Home Menu',
          'CBA841B50A92A904E313AE06DF4EF71A':'Splatoon 2',
          '1628E0CE3F839127054B0EE36E28E52A':'Sonic Mania',
          '93FA958835AC3573C5186D5F5B0DB6B2':'Cave Story+',
          '16851BE00BC6068871FE49D98876D6C5':'Mario Kart 8 Deluxe',
          'F8D087CFC849713C76A06A954E9486D3':'Shovel Knight',
          'C4E9854DE59E1AAD6BFE8091E8A5B77D':'World of Goo',
          '291F8A44D0318835B09A30B3A1A99B6A':'Metal Slug 3',
          'C31DA8706A6CDDCC04A04CFA35F47298':'Project Octopath Demo',
          'D6F3EB1178A90392C0B8A57476DADED0':'Axiom Verge',
          'C2B49A475DF5A340494292A1BD398579':'Stardew Valley',
          '28D351544DC829EEBE54E53AF29EB030':'PAN-PAN',
          '412E0591DD033E78737A4B6DC2C70E50':'ARMS Global Testpunch',
          '539D575B96E556159C3F4667D1100DDD':'Picross S',
          '6F4D679ED7D2A016B654B265B956C5F0':'Rocket League',
          '993AC1F3383F4FF879FEA9A85677F9F9':'VVVVVV',
          '1AB131B6E6571375B79964211BB3F5AE':'Error Overlay'
          }

parser = argparse.ArgumentParser(
    description='Automatically organize and timestamp\
                 your Nintendo Switch captures.')

parser.add_argument(
    'filepath',
    metavar='FILEPATH',
    type=Path,
    help='"Nintendo/Album" folder from your SD card.')

# If there are arguments, parse them. If not, exit
if (len(sys.argv) > 1):
    args = parser.parse_args()
else:
    print('No folder specified! Exitting...')
    sys.exit()

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

        #print("Game ID: {}".format(checkID(gameid,idname)))
        #print("{}:{}:{}".format(hour, minute, second))
        time = datetime(
                        int(year),
                        int(month),
                        int(day),
                        hour=int(hour),
                        minute=int(minute),
                        second=int(second))
        posixtimestamp = time.timestamp()
        #print(time)
        #print(posixtimestamp)

        outputfolder = args.filepath.joinpath('Organized', checkID(gameid,idname))

        outputfolder.mkdir(parents=True, exist_ok=True)

        newfile = copy(mediapath, outputfolder)

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