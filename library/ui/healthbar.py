"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import colorsys
import math

import pygame

from game.utils import load_font
from library.particles import TextParticle


class PlayerHealthBar:
    def __init__(
        self,
        entity,
        particle_manager,
        pos,
        width: int,
        height: int,
        border_width: int = 2,
        center=False,
    ):
        self.uuid = None
        self.entity = entity
        self.particle_manager = particle_manager

        self.pos = pos
        self.width = width
        self.height = height
        self.border_width = border_width

        self.border_rect = pygame.Rect(
            self.pos[0] - border_width,
            self.pos[1] - border_width,
            width + 2 * border_width,
            height + 2 * border_width,
        )
        self.rect = pygame.Rect(
            *self.pos, self.entity.hp / self.entity.max_hp * width, height
        )

        self.previous_health = self.entity.hp
        self.flash_size = 0
        self.flash_duration = -1
        self.flash_width = 0
        self.flash_hp_diff = 0  # 1 for lost, -1 for gained

        self.hurt_font = load_font(8)

        if center:
            self.rect.center = pos
            self.border_rect.topleft = (
                self.rect.topleft[0] - border_width,
                self.rect.topleft[1] - border_width,
            )

    def draw(self, screen):
        self.flash_duration -= 1
        self.rect.width = self.entity.hp / self.entity.max_hp * self.width

        hp_percentage = self.rect.width / self.width
        hsv = (hp_percentage / 3, 1, 1)
        rgb = colorsys.hsv_to_rgb(*hsv)
        hp_color = [max(int(color_value * 255), 0) for color_value in rgb]

        hp_lost = self.previous_health - self.entity.hp
        self.flash_size += abs(hp_lost)

        if hp_lost != 0:
            hurt_txt = f"{(-hp_lost):+} HP"
            if self.entity.hp > 0:
                self.flash_duration = 10
            else:
                self.flash_duration = 40
            self.flash_hp_diff = math.copysign(1, hp_lost)

            self.particle_manager.add(
                TextParticle(
                    screen=screen,
                    image=self.hurt_font.render(hurt_txt, True, (180, 32, 42)),
                    pos=self.entity.vec,
                    vel=(0, -1.5),
                    alpha_speed=3,
                    lifespan=80,
                )
            )

        if self.flash_duration <= 0:
            if self.entity.hp > 0:
                self.flash_size -= 1
                self.flash_size *= 0.98
                self.flash_size = max(0, self.flash_size - 1.5)
            else:
                self.flash_size -= 1 / 4
                self.flash_size *= 0.985
                self.flash_size = max(0, self.flash_size)

        pygame.draw.rect(
            screen, (69, 69, 69), self.border_rect, width=self.border_width
        )
        pygame.draw.rect(screen, hp_color, self.rect)

        self.flash_width = self.flash_size * self.width / self.entity.max_hp

        if self.flash_width > 0:
            flash_rect = pygame.Rect(
                self.rect.x + self.rect.width,
                self.rect.y,
                self.flash_width,
                self.height,
            )

            if self.flash_hp_diff == -1:
                flash_rect.right = self.rect.right

            pygame.draw.rect(screen, (255, 255, 255), flash_rect)
        else:
            self.flash_hp_diff = 0

        self.previous_health = self.entity.hp
