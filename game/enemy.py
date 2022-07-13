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
    def __init__(self, settings: dict, obj, max_hp=None):
        super().__init__(settings, max_hp)

        self.speed = obj.speed
        self.size = (int(obj.width), int(obj.height))
        self.rect = pygame.Rect((obj.x, obj.y), self.size)
        self.name = obj.name

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
    def __init__(self, settings: dict, obj, assets: dict):
        super().__init__(settings, obj)

        self.wander_point_a = tile_to_pixel(string_pos_to_tuple(obj.wander_point_a))
        self.wander_point_b = tile_to_pixel(string_pos_to_tuple(obj.wander_point_b))

        self.last_turned = 0

        img = assets["moving_wall"]
        self.surf = pygame.Surface(self.size)

        _range = int(self.size[1] / img.get_height())
        for y in range(_range):
            self.surf.blit(img, (0, (y * img.get_height())))

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
        # pygame.draw.rect(
        #     screen, (42, 45, 55), (camera.apply(self.rect).topleft, self.rect.size)
        # )
        screen.blit(self.surf, camera.apply(self.rect).topleft)
        # pygame.draw.rect(screen, (42, 45, 55), (0, 0, self.rect.width, self.rect.height))


class MovingPlatform(Enemy):
    def __init__(self, settings: dict, obj, tileset):
        super().__init__(settings, obj)

        self.wander_point_a = tile_to_pixel(string_pos_to_tuple(obj.wander_point_a))
        self.wander_point_b = tile_to_pixel(string_pos_to_tuple(obj.wander_point_b))

        self.last_turned = 0

        self.placeholder_surf = pygame.Surface(self.size)
        self.placeholder_surf.fill((128, 128, 128))

        self.surf = self.assemble_img(tileset)

    def assemble_img(self, tileset):
        temp_surf = pygame.Surface(self.size, pygame.SRCALPHA)

        tile_width, tile_height = (
            self.size[0] // TILE_WIDTH,
            self.size[1] // TILE_HEIGHT,
        )
        corners = {
            (0, 0): 0,
            (tile_width - 1, 0): 2,
            (0, tile_height - 1): 8,
            (tile_width - 1, tile_height - 1): 10,
        }

        for y in range(tile_height):
            for x in range(tile_width):
                if (x, y) in corners:
                    tile_id = corners[(x, y)]
                elif x == 0:
                    tile_id = 4
                elif y == 0:
                    tile_id = 1
                elif x == tile_width - 1:
                    tile_id = 6
                elif y == tile_height - 1:
                    tile_id = 9
                else:
                    tile_id = 5

                temp_surf.blit(tileset[tile_id], (x * TILE_WIDTH, y * TILE_HEIGHT))

        return temp_surf

    def update(self, event_info: EventInfo, tilemap, player, shooters) -> None:
        self.vel.x = 0

        dt = event_info["dt"]

        self.vel.x = self.speed * dt * self.facing.value

        for movable in {player}.union(shooters):
            movable_rect = movable.rect.copy()
            movable_rect.y += 5
            if movable_rect.colliderect(self.rect):
                movable.rect.x += round(self.vel.x)
            
            movable_rect.y -= 10
            if movable_rect.colliderect(self.rect):
                movable.rect.x += round(self.vel.x)

        self.rect.x += round(self.vel.x)

        # Update position attributes to rect.topleft
        self.vec.x, self.vec.y = self.rect.topleft
        self.tile_vec = pixel_to_tile(self.vec)

        if self.facing == EntityFacing.RIGHT:
            check_x = self.rect.right
            adj_wander_point_b = self.wander_point_b[0] + TILE_WIDTH
        else:
            check_x = self.rect.x
            adj_wander_point_b = self.wander_point_b[0]

        # Sometimes the platform get stuck, hence the last turned check
        if (
            not self.wander_point_a[0] < check_x < adj_wander_point_b
            and pygame.time.get_ticks() - self.last_turned > 500
        ):
            self.facing = EntityFacing(-self.facing.value)
            self.last_turned = pygame.time.get_ticks()

    def draw(self, dt: float, screen: pygame.Surface, camera):
        screen.blit(self.surf, camera.apply(self.rect).topleft)


class Ungrappleable:
    def __init__(self, obj):
        self.size = (int(obj.width), int(obj.height))
        self.rect = pygame.Rect((obj.x, obj.y), self.size)
        self.name = obj.name