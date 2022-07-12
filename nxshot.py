import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime
from shutil import copy

from Crypto.Cipher import AES
import hashlib

from urllib.request import urlopen, urlretrieve
from urllib.error import URLError
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

KEY_HASH = "24e0dc62a15c11d38b622162ea2b4383"
IS_UPDATED = 0
ENCRYPTED_IDS = {}

# Argument parser
parser = argparse.ArgumentParser(
    description='Automatically organize and timestamp\
                 your Nintendo Switch captures.')

parser.add_argument(
    'filepath',
    metavar='FILEPATH',
    type=Path,
    help='"Nintendo/Album" folder from your SD card.')

parser.add_argument('-d',
                    '--download-nswdb',
                    action='store_true',
                    help='Download IDs from nswdb.com instead of switchbrew.org\n \
          NOTE: Regions may not match')

# If there are arguments, parse them. If not, exit
args = parser.parse_args()


def load_key(file_name, KEY_HASH):
    try:
        with open(file_name, 'r') as key_file:
            key_string = key_file.read(32)
            key = bytes.fromhex(key_string)
            if(hashlib.md5(key).hexdigest() not in KEY_HASH):
                raise ValueError("Keys don't match!")
            return key

    except FileNotFoundError:
        print("Encryption key (key.txt) not found!")
    except ValueError:
        print("Encryption key (key.txt) doesn't match!")


def encrypt_title_id(key, title_id):
    key_cipher = AES.new(key, AES.MODE_ECB)

    title_id_bytes = bytearray.fromhex(title_id[:16])
    title_id_bytes.reverse()
    title_id_bytes = title_id_bytes.ljust(16, b'\0')  # Padding

    encrypted_title_id = key_cipher.encrypt(title_id_bytes)
    screenshot_id = encrypted_title_id.hex().upper()

    return screenshot_id


def update_game_ids():
    key = load_key('key.txt', KEY_HASH)
    if not key:
        return -1

    if args.download_nswdb:
        update_nswdb(key)
    else:
        update_switchbrew(key)

    with open('gameids.json', 'w', encoding='utf-8') as encrypted_ids_file:
        json.dump(ENCRYPTED_IDS, encrypted_ids_file,
                  ensure_ascii=False, indent=4, sort_keys=True)
        print("Successfully IS_UPDATED Game IDs")

    return 1


def update_switchbrew(key):
    wiki = 'http://switchbrew.org/index.php?title=Title_list/Games'
    try:
        wiki_page = urlopen(wiki)
    except URLError:
        print("Could not update gameids!")
        return -1

    wiki_soup = BeautifulSoup(wiki_page, 'html.parser')
    game_table = wiki_soup.find('table', {"class": "wikitable sortable"})
    game_table_rows = game_table.find_all('tr')

    for row in game_table_rows[1:]:
        try:
            title_id = str(row.contents[1].string)
            game_name = str(row.contents[3].string)
            region = str(row.contents[5].string)
        except IndexError:  # At least one cell empty; ignore row
            continue

        if title_id == 'None' or game_name == 'None' or region == 'None':
            continue

        if ":" in game_name:
            game_name = game_name.replace(":", " -")

        #print('TitleID = {}'.format(title_id))

        screenshot_id = encrypt_title_id(key, title_id)

        #print("ScreenshotID = {}".format(encrypted.hex()))
        ENCRYPTED_IDS[screenshot_id] = game_name + ' (' + region + ')'


def update_nswdb(key):
    urlretrieve('http://nswdb.com/xml.php', 'db.xml')
    tree = ET.parse('db.xml')
    root = tree.getroot()

    for release in root.findall('release'):
        try:
            screenshot_id = encrypt_title_id(key, release.find('titleid').text)

            region = release.find('region').text
            if region == "WLD":
                region = "EUR USA"

            name = release.find('name').text
            name = name.replace(":", " -")
        except ValueError:
            continue

        ENCRYPTED_IDS[screenshot_id] = name + ' (' + region + ')'

    os.remove("db.xml")


def check_id(game_id, ENCRYPTED_IDS):
    if game_id in ENCRYPTED_IDS:
        return ENCRYPTED_IDS[game_id]
    else:
        return 'Unknown'


def check_folders(file_list):
    current = 0
    length = len(file_list)
    # print(file_list)
    for media_path in file_list:
        year = media_path.stem[0:4]
        month = media_path.stem[4:6]
        day = media_path.stem[6:8]
        hour = media_path.stem[8:10]
        minute = media_path.stem[10:12]
        second = media_path.stem[12:14]
        game_id = media_path.stem[17:]

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
                    str(media_path.stem)
                )
            )
            continue

        posix_timestamp = time.timestamp()

        output_folder = args.filepath.joinpath(
            'Organized', check_id(game_id, ENCRYPTED_IDS))

        output_folder.mkdir(parents=True, exist_ok=True)

        new_file = copy(str(media_path), str(output_folder))

        os.utime(new_file, (posix_timestamp, posix_timestamp))

        current += 1

        print('Organized {} of {} files.\r'.format(current, length), end='')
    print("")


# Load game ids and their names from external file
try:
    with open('gameids.json', 'r', encoding='utf-8') as encrypted_ids_file:
        ENCRYPTED_IDS = json.load(encrypted_ids_file)
except FileNotFoundError:
    print('Game ID list (gameids.json) not found! Fetching from Switchbrew...')
    IS_UPDATED = update_game_ids()
    if IS_UPDATED < 0:
        sys.exit()
except json.decoder.JSONDecodeError:
    print('Invalid JSON format! Fetching from Switchbrew...')
    IS_UPDATED = update_game_ids()
    if IS_UPDATED < 0:
        sys.exit()

if not IS_UPDATED:
    update_game_ids()

album_folder = args.filepath

screenshot_list = sorted(
    Path(album_folder).glob(
        '[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]/*.jpg'
    )
)

video_list = sorted(
    Path(album_folder).glob(
        '[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]/*.mp4'
    )
)

if len(screenshot_list) != 0:
    print('Organizing screenshots...')
    check_folders(screenshot_list)
else:
    print('No screenshots found!')

if len(video_list) != 0:
    print('\nOrganizing videos...')
    check_folders(video_list)
else:
    print('\nNo videos found!')

print('Done!')
