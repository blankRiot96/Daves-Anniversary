"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import pathlib

import pygame
import pytmx as pytmx

from .tiles import Tile


class TileLayerMap:
    """
    Adds some functions like render_map and make_map to enhance pytmx's tilemap
    """

    def __init__(self, map_path: pathlib.Path):
        self.tilemap = pytmx.load_pygame(str(map_path))
        self.width = self.tilemap.width * self.tilemap.tilewidth
        self.height = self.tilemap.height * self.tilemap.tileheight

        # Tiles will be filled in on render_map
        self.tiles = {}

    def render_map(self, surface: pygame.Surface) -> None:
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

                    tile_img = self.tilemap.get_tile_image_by_gid(gid)
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


    def make_map(self) -> pygame.Surface:
        """
        Makes a pygame.Surface, then render the map and return the rendered map

        Returns:
            A pygame.Surface to blit to the main screen
        """

        temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.render_map(temp_surface)
        return temp_surface
