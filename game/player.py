"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""
import typing

import pygame

from game.common import EventInfo
from game.utils import get_neighboring_tiles, pixel_to_tile


# TODO: Make Player a pygame.sprite.Sprite
class Player:
    """
    Handles player
    """

    SIZE = (32, 32)
    SPEED = 2.4
    SPACE_KEYS = pygame.K_w, pygame.K_SPACE

    def __init__(self):
        self.alive = True
        self.image = pygame.Surface(self.SIZE)
        self.image.fill("red")
        self.rect = pygame.Rect((0, 0), self.SIZE)

        self.x, self.y = 0, 0
        self.vec = pygame.Vector2()
        self.tile_vec = pygame.Vector2()

        self.vel = pygame.Vector2()
        self.gravity_acc = 0.3
        self.touched_ground = True

    def handle_player_input(self, event_info: EventInfo) -> None:
        """
        Handle the player's key presses

        Parameters:
            event_info: Information on the window events
        """

        dt = event_info["dt"]
        keys = event_info["key_press"]
        if keys[pygame.K_d]:
            self.vel.x = self.SPEED * dt
        if keys[pygame.K_a]:
            self.vel.x = -self.SPEED * dt

        for event in event_info["events"]:
            if event.type == pygame.KEYDOWN:
                if event.key in self.SPACE_KEYS and self.touched_ground:
                    self.vel.y = -9
                    self.touched_ground = False

    def update(self, event_info: EventInfo, tilemap) -> None:
        """
        Updates the player class
        Handles key input

        Parameters:
            event_info: Information on the window events
            tilemap: Tilemap to get neighboring tiles
        """

        # Resets self.vel.x
        self.vel.x = 0

        dt = event_info["dt"]
        self.handle_player_input(event_info)
        self.handle_tile_collisions(
            dt, get_neighboring_tiles(tilemap, 1, self.tile_vec)
        )

        # Add gravity
        self.vel.y += self.gravity_acc * dt

        # Update position attributes to rect.topleft
        self.vec.x, self.vec.y = self.rect.topleft
        self.x = self.rect.x
        self.y = self.rect.y
        self.tile_vec = pixel_to_tile(self.vec)

    def draw(self, screen: pygame.Surface, camera) -> None:
        """
        Draws the player

        Parameters:
            screen: pygame.Surface to draw player on
            camera: camera.Camera to adjust position
        """

        screen.blit(self.image, camera.apply(self.vec))

    def handle_tile_collisions(
        self, dt: float, neighboring_tiles: typing.List[typing.Any]
    ) -> None:
        """
        Handles the tile collision

        Parameters:
            dt: the deltatime for framerate independent movement
            neighboring_tiles: the player's current closest tiles
        """

        self.rect.x += round(self.vel.x * dt)

        for neighboring_tile in neighboring_tiles:
            if neighboring_tile.rect.colliderect(self.rect):
                if self.vel.x > 0:
                    self.rect.right = neighboring_tile.rect.left
                elif self.vel.x < 0:
                    self.rect.left = neighboring_tile.rect.right

        self.rect.y += round(self.vel.y * dt)

        for neighboring_tile in neighboring_tiles:
            if neighboring_tile.rect.colliderect(self.rect):
                if self.vel.y > 0:
                    self.vel.y = 0
                    self.touched_ground = True
                    self.rect.bottom = neighboring_tile.rect.top
                elif self.vel.y < 0:
                    self.vel.y = 0
                    self.rect.top = neighboring_tile.rect.bottom
