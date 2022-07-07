"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""
import json
import pathlib
import typing

import pygame

from game.common import TILE_HEIGHT, TILE_WIDTH
from library.tilemap import TileLayerMap


def pixel_to_tile(
    pixel_pos: typing.Union[tuple, pygame.Vector2],
    tile_width: int = TILE_WIDTH,
    tile_height: int = TILE_HEIGHT,
) -> pygame.Vector2:
    """
    Maps a pixel coordinate to a tile coordinate

    Parameters:
        pixel_pos: The pixel coordinate
        tile_width: The tile width. Defaults to common.TILE_WIDTH
        tile_height: The tile height. Defaults to common.TILE_HEIGHT
    """

    if isinstance(pixel_pos, tuple):
        pixel_pos = pygame.Vector2(*pixel_pos)

    return pygame.Vector2(
        round(pixel_pos.x / tile_width), round(pixel_pos.y / tile_height)
    )


def tile_to_pixel(
    tile_pos: typing.Union[tuple, pygame.Vector2],
    tile_width: int = TILE_WIDTH,
    tile_height: int = TILE_HEIGHT,
) -> pygame.Vector2:
    """
    Maps a tile coordinate to a pixel coordinate

    Parameters:
        tile_pos: The tile coordinate
        tile_width: The tile width. Defaults to common.TILE_WIDTH
        tile_height: The tile height. Defaults to common.TILE_HEIGHT
    """

    if isinstance(tile_pos, tuple):
        tile_pos = pygame.Vector2(*tile_pos)

    return pygame.Vector2(tile_pos.x * tile_width, tile_pos.y * tile_height)


def get_neighboring_tiles(
    tilemap: TileLayerMap, radius: int, tile_pos: pygame.Vector2
) -> typing.List[typing.Any]:
    """
    Gets the nearest `radius` tiles from `tile_pos`

    Parameters:
        tilemap: The tilemap class to extract the information
        radius: The desired radius of tiles to include
        tile_pos: The tile position
    """
    neighboring_tile_entities = []

    for x in range(int(tile_pos.x) - radius, int(tile_pos.x) + radius + 1):
        for y in range(int(tile_pos.y) - radius, int(tile_pos.y) + radius + 1):
            try:
                tile = tilemap.tiles[(x, y)]
            except KeyError:
                # Outside map boundaries (for some reason)
                continue

            neighboring_tile_entities.append(tile)

    return neighboring_tile_entities


def load_settings(path: pathlib.Path) -> dict:
    with open(path) as f:
        settings = json.load(f)

    return settings


def string_pos_to_tuple(string: str) -> tuple:
    string_split = string.replace("(", "").replace(")", "").split(",")
    return int(string_split[0]), int(string_split[1])
