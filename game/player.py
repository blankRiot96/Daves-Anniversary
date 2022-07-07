"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""
import typing

import pygame

from game.common import TILE_HEIGHT, TILE_WIDTH, EventInfo
from game.entity import Entity, EntityStates, EntityFacing
from game.utils import get_neighboring_tiles, pixel_to_tile
from library.utils.animation import Animation
from library.utils.funcs import flip_images


# TODO: Make Player a pygame.sprite.Sprite
class Player(Entity):
    """
    Handles player
    """

    SIZE = (10, 16)
    WALK_ANIM_SPEED = 0.05
    SPACE_KEYS = pygame.K_w, pygame.K_SPACE

    def __init__(self, settings: dict, walk_frames: typing.List[pygame.Surface]):
        super().__init__(settings)

        self.alive = True
        self.animations = {
            "walk_right": Animation(walk_frames, self.WALK_ANIM_SPEED),
            "walk_left": Animation(flip_images(walk_frames), self.WALK_ANIM_SPEED),
        }
        self.speed = settings["player_speed"]
        self.jump_height = settings["player_jump"]

        self.rect = pygame.Rect((0, 0), self.SIZE)

    def handle_player_input(self, event_info: EventInfo) -> None:
        """
        Handle the player's key presses

        Parameters:
            event_info: Information on the window events
        """

        dt = event_info["dt"]
        keys = event_info["key_press"]
        self.state = EntityStates.IDLE
        if keys[pygame.K_d]:
            self.vel.x = self.speed * dt
            self.state = EntityStates.WALK
            self.facing = EntityFacing.RIGHT
        if keys[pygame.K_a]:
            self.vel.x = -self.speed * dt
            self.state = EntityStates.WALK
            self.facing = EntityFacing.LEFT

        for event in event_info["events"]:
            if event.type == pygame.KEYDOWN:
                if event.key in self.SPACE_KEYS and self.touched_ground:
                    self.vel.y = self.jump_height
                    self.touched_ground = False

        # if we are in the air
        if not self.touched_ground:
            self.state = EntityStates.JUMP

    def update(self, event_info: EventInfo, tilemap, enemies) -> None:
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

        min_tile_size = max(self.SIZE[0] // TILE_WIDTH + 5, self.SIZE[1] // TILE_HEIGHT + 5)
        collidable_rects = get_neighboring_tiles(tilemap, min_tile_size, self.tile_vec)

        # NGL, I added this because it fixes the y collision with the enemies
        for enemy in enemies:
            collidable_rects.append(enemy)

        self.handle_tile_collisions(
            collidable_rects
        )

        # Add and cap gravity
        self.vel.y += self.gravity_acc * dt
        self.vel.y = min(17, self.vel.y)

        # Update position attributes to rect.topleft
        self.vec.x, self.vec.y = self.rect.topleft
        self.tile_vec = pixel_to_tile(self.vec)

    def draw(self, dt: float, screen: pygame.Surface, camera) -> None:
        """
        Draws the player

        Parameters:
            dt: the deltatime for framerate independent movement
            screen: pygame.Surface to draw player on
            camera: camera.Camera to adjust position
        """
        animation = self.animations[f"walk_{self.facing.name.lower()}"]

        if self.state == EntityStates.WALK:
            animation.play(screen, camera.apply(self.vec).topleft, dt)
        else:
            screen.blit(animation.frames[0], camera.apply(self.vec))
