"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import pathlib
import typing
import json 

# Generics

EventInfo = typing.Dict[str, typing.Any]

# Game stuff
WIDTH = 600
HEIGHT = 320

TILE_WIDTH = 16
TILE_HEIGHT = 16

# Paths
ROOT_DIR = pathlib.Path(".")
ASSETS_DIR = ROOT_DIR / "assets"
DATA_DIR = ASSETS_DIR / "data"
AUDIO_DIR = ASSETS_DIR / "audio"
MAP_DIR = ASSETS_DIR / "maps"
FONT_DIR = ASSETS_DIR / "fonts"
SETTINGS_DIR = DATA_DIR / "settings"

with open(DATA_DIR / "save.json") as f:
    SAVE_DATA = json.load(f)
