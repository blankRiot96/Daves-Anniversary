"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import abc
import enum
import typing

import pygame

from game.common import EventInfo


class Entity(abc.ABC):
    def __init__(self, settings: dict):
        self.settings = settings

        self.rect = pygame.Rect(0, 0, 0, 0)  # Placeholder, derived class overwrite

        # can be "right" or "left"
        self.facing = EntityFacing.RIGHT
        self.state = EntityStates.IDLE

        self.vec = pygame.Vector2()
        self.tile_vec = pygame.Vector2()

        self.vel = pygame.Vector2()
        self.touched_ground = True
        self.alive = True

        self.gravity_acc = self.settings["gravity"]
    
    def handle_tile_collisions(
        self, neighboring_tiles: typing.List[typing.Any]
    ) -> None:
        """
        Handles the tile collision

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

    @property
    def x(self):
        return self.vec.x
    
    @property
    def y(self):
        return self.vec.y

    @abc.abstractmethod
    def update(self, event_info: EventInfo, tilemap) -> None:
        pass

    @abc.abstractmethod
    def draw(self, dt: float, screen: pygame.Surface, camera) -> None:
        pass



class EntityStates(enum.Enum):
    WALK = enum.auto()
    IDLE = enum.auto()
    JUMP = enum.auto()


class EntityFacing(enum.Enum):
    RIGHT = 1
    LEFT = -1
