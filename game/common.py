"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import pathlib
import typing

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
MAP_DIR = ASSETS_DIR / "maps"

SETTINGS_DIR = DATA_DIR / "settings"
