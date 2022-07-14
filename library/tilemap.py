"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

from multiprocessing.sharedctypes import Value
import pathlib
import typing
from typing import Optional, Sequence

import pygame
import pytmx 

from .tiles import SpikeTile, Tile

class TileLayerMap:
    """
    Adds some functions like render_map and make_map to enhance pytmx's tilemap
    """

    def __init__(self, map_path: pathlib.Path):
        def overwritten_get_layer_by_name(name: str):
            try:
                return self.tilemap.layernames[name]
            except KeyError:
                return ()

        self.tilemap = pytmx.load_pygame(str(map_path))

        self.tilemap.get_layer_by_name = overwritten_get_layer_by_name

        self.width = self.tilemap.width * self.tilemap.tilewidth
        self.height = self.tilemap.height * self.tilemap.tileheight

        # Tiles will be filled in on render_map
        self.tiles = {}
        self.special_tiles = {}

    def render_map(
        self, surface: pygame.Surface, tilset: Optional[Sequence] = None
    ) -> None:
        """
        Renders the map to a given surface

        Parameters:
            surface: pygame.Surface to blit on
        """

        # surface.set_colorkey((0, 0, 0))

        for layer_id, layer in enumerate(self.tilemap.visible_layers):
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    # Gets tile properties
                    tile_props = self.tilemap.get_tile_properties_by_gid(gid)
                    if tile_props is None:
                        continue

                    if tilset is None:
                        tile_img = self.tilemap.get_tile_image_by_gid(gid)
                    else:
                        tile_img = tilset[tile_props["id"]]
                    tile_instance = None

                    # Blit the tile image to surface
                    surface.blit(
                        tile_img,
                        (x * self.tilemap.tilewidth, y * self.tilemap.tileheight),
                    )

                    # Construct appropriate instance based on tile type
                    if tile_props["class"] == "tile":
                        tile_instance = Tile(
                            tile_img,
                            (x * self.tilemap.tilewidth, y * self.tilemap.tileheight),
                        )

                        # Add tile instance to self.tiles
                        self.tiles[(x, y)] = tile_instance

                    if tile_props.get("special_type") == "spike":
                        tile_instance = SpikeTile(
                            tile_img,
                            (x * self.tilemap.tilewidth, y * self.tilemap.tileheight),
                        )

                        self.special_tiles[(x, y)] = tile_instance


    def make_map(self, tileset: Optional[Sequence] = None) -> pygame.Surface:
        """
        Makes a pygame.Surface, then render the map and return the rendered map

        Returns:
            A pygame.Surface to blit to the main screen
        """

        temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.render_map(temp_surface, tileset)
        return temp_surface
