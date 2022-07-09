"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import typing

import pygame

from game.common import TILE_HEIGHT, TILE_WIDTH, EventInfo
from game.entity import Entity, EntityFacing
from game.utils import (get_neighboring_tiles, pixel_to_tile,
                        string_pos_to_tuple, tile_to_pixel)


class Enemy(Entity):
    def __init__(self, settings: dict, obj):
        super().__init__(settings)

        self.speed = obj.speed
        self.size = (int(obj.width), int(obj.height))
        self.rect = pygame.Rect((obj.x, obj.y), self.size)

    def handle_collision(
        self, neighboring_tiles: typing.List[typing.Any], player
    ) -> None:
        """
        Handles the collision, including tiles and player.

        Parameters:
            dt: the deltatime for framerate independent movement
            neighboring_tiles: the player's current closest tiles
        """

        self.rect.x += round(self.vel.x)

        for neighboring_tile in neighboring_tiles:
            if neighboring_tile.rect.colliderect(self.rect):
                if self.vel.x > 0:
                    self.rect.right = neighboring_tile.rect.left
                elif self.vel.x < 0:
                    self.rect.left = neighboring_tile.rect.right

        if player.rect.colliderect(self.rect):
            if self.vel.x > 0:
                player.rect.left = self.rect.right
            elif self.vel.x < 0:
                player.rect.right = self.rect.left

        self.rect.y += round(self.vel.y)

        for neighboring_tile in neighboring_tiles:
            if neighboring_tile.rect.colliderect(self.rect):
                if self.vel.y > 0:
                    self.vel.y = 0
                    self.touched_ground = True
                    self.rect.bottom = neighboring_tile.rect.top
                elif self.vel.y < 0:
                    self.vel.y = 0
                    self.rect.top = neighboring_tile.rect.bottom

        if player.rect.colliderect(self.rect):
            if self.vel.y > 0:
                player.vel.y = 0
                player.touched_ground = True
                player.rect.top = self.rect.bottom
            elif self.vel.y < 0:
                player.vel.y = 0
                player.rect.bottom = self.rect.top


class MovingWall(Enemy):
    def __init__(self, settings: dict, obj):
        super().__init__(settings, obj)

        self.wander_point_a = tile_to_pixel(string_pos_to_tuple(obj.wander_point_a))
        self.wander_point_b = tile_to_pixel(string_pos_to_tuple(obj.wander_point_b))

        self.last_turned = 0

    def update(self, event_info: EventInfo, tilemap, player) -> None:
        self.vel.x = 0

        dt = event_info["dt"]

        self.vel.x = self.speed * dt * self.facing.value

        min_tile_size = max(
            self.size[0] // TILE_WIDTH + 5, self.size[1] // TILE_HEIGHT + 5
        )
        self.handle_collision(
            get_neighboring_tiles(tilemap, min_tile_size, self.tile_vec), player
        )

        # Add and cap gravity
        self.vel.y += self.gravity_acc * dt
        self.vel.y = min(17, self.vel.y)

        # Update position attributes to rect.topleft
        self.vec.x, self.vec.y = self.rect.topleft
        self.tile_vec = pixel_to_tile(self.vec)

        # Sometimes the walls get stuck, hence the last turned check
        if (
            not self.wander_point_a[0] < self.vec.x < self.wander_point_b[0]
            and pygame.time.get_ticks() - self.last_turned > 500
        ):
            self.facing = EntityFacing(-self.facing.value)
            self.last_turned = pygame.time.get_ticks()

    def draw(self, dt: float, screen: pygame.Surface, camera):
        # Placeholder
        pygame.draw.rect(
            screen, (42, 45, 55), (camera.apply(self.rect).topleft, self.rect.size)
        )
        # pygame.draw.rect(screen, (42, 45, 55), (0, 0, self.rect.width, self.rect.height))
