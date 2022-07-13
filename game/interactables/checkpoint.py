"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import pygame

from game.interactables.abc import Interactable
from game.utils import load_font
from library.common import Pos
from library.particles import TextParticle


class Checkpoint:
    FONT = load_font(16)

    def __init__(self, rect, particle_manager, unlock_dimension, c_id):
        self.rect = rect

        self.particle_manager = particle_manager
        self.text_spawned = False
        self.unlock_dimension = unlock_dimension
        self.id = c_id

        # GOOFY
        self.screen = None

    def update(self, player_rect, latest_checkpoint_id):
        if not self.text_spawned and self.rect.colliderect(player_rect) and (self.id > latest_checkpoint_id or self.id == 0):
            self.text_spawned = True

            self.particle_manager.add(
                TextParticle(
                    screen=self.screen,
                    image=self.FONT.render(
                        "Checkpoint reached!", True, (255, 255, 255)
                    ),
                    pos=player_rect.midtop,
                    vel=(0, -2),
                    alpha_speed=3,
                    lifespan=100,
                )
            )

    def draw(self, screen):
        # GOOFY
        self.screen = screen
