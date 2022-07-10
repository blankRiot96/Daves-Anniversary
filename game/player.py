"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""
import typing

import pygame

from game.common import TILE_HEIGHT, TILE_WIDTH, EventInfo
from game.entity import Entity, EntityFacing, EntityStates
from game.items.grapple import Grapple, Swing
from game.utils import get_neighboring_tiles, pixel_to_tile
from library.effects.explosions import ExplosionManager
from library.utils.animation import Animation
from library.utils.funcs import flip_images


# TODO: Make Player a pygame.sprite.Sprite
class Player(Entity):
    """
    Handles player
    """

    MAX_HP = 100
    SIZE = (10, 16)
    WALK_ANIM_SPEED = 0.05
    SPACE_KEYS = pygame.K_w, pygame.K_SPACE

    def __init__(
        self,
        settings: dict,
        walk_frames: typing.List[pygame.Surface],
        camera,
        particle_manager,
    ):
        super().__init__(settings)
        # set player stats
        self.change_settings(settings)

        self.alive = True
        self.animations = {
            "walk_right": Animation(walk_frames, self.WALK_ANIM_SPEED),
            "walk_left": Animation(flip_images(walk_frames), self.WALK_ANIM_SPEED),
        }
        self.animation = None
        self.speed = settings["player_speed"]
        self.jump_height = settings["player_jump"]

        self.camera = camera
        self.particle_manager = particle_manager

        self.rect = pygame.Rect((0, 0), self.SIZE)
        self.jump_exp = ExplosionManager("smoke-jump")
        self.is_jump = False

        self.grapple = Grapple(self, self.camera, self.particle_manager)

        self.hp = self.MAX_HP

    def change_settings(self, settings: dict) -> None:
        self.speed = settings["player_speed"]
        self.jump_height = settings["player_jump"]
        self.gravity_acc = settings["gravity"]

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

        self.is_jump = False
        for event in event_info["events"]:
            if event.type == pygame.KEYDOWN:
                if event.key in self.SPACE_KEYS and self.touched_ground:
                    self.is_jump = True
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

        min_tile_size = max(
            self.SIZE[0] // TILE_WIDTH + 5, self.SIZE[1] // TILE_HEIGHT + 5
        )
        collidable_rects = get_neighboring_tiles(tilemap, min_tile_size, self.tile_vec)

        # NGL, I added this because it fixes the y collision with the enemies
        for enemy in enemies:
            collidable_rects.append(enemy)

        # Add and cap gravity
        self.vel.y += self.gravity_acc * dt
        self.vel.y = min(17, self.vel.y)

        # self.swing.update(event_info, tilemap, enemies)
        self.grapple.update(event_info, tilemap, enemies)

        self.handle_tile_collisions(collidable_rects)

        # Update position attributes to rect.topleft
        self.vec.x, self.vec.y = self.rect.topleft
        self.tile_vec = pixel_to_tile(self.vec)

        # Jump exp
        self.jump_exp.update(dt)

        # Animation
        self.animation = self.animations[f"walk_{self.facing.name.lower()}"]
        self.animation.update(dt)

    def handle_jump_exp(self, screen, camera):
        if self.is_jump:
            self.jump_exp.create_explosion(camera.apply(self.vec).topleft)
        self.jump_exp.draw(screen)

    def draw(self, screen: pygame.Surface, camera) -> None:
        """
        Draws the player

        Parameters:
            dt: the deltatime for framerate independent movement
            screen: pygame.Surface to draw player on
            camera: camera.Camera to adjust position
        """
        self.handle_jump_exp(screen, camera)
        # self.swing.draw(screen)
        self.grapple.draw(screen)

        animation = self.animations[f"walk_{self.facing.name.lower()}"]

        if self.state == EntityStates.WALK:
            animation.draw(screen, camera.apply(self.vec).topleft)
        else:
            screen.blit(animation.frames[0], camera.apply(self.vec))
