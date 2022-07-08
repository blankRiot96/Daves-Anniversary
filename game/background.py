"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import math
import random

import pygame

from game.common import HEIGHT, WIDTH
from library.utils.classes import Time
from library.utils.funcs import get_movement


class _Line:
    LINE_WIDTH = 5

    def __init__(self, num) -> None:
        self.start_pos = pygame.Vector2(num, HEIGHT)
        self.end_pos = pygame.Vector2(WIDTH, num)
        self.alive = True
        self.distance_travelled = 0

    def update(self):
        changed = pygame.Vector2(get_movement(240, 0.3))
        self.start_pos += changed
        self.end_pos += changed

        self.distance_travelled += math.sqrt(((changed.x**2) + (changed.y**2)))

        if self.distance_travelled > HEIGHT:
            self.alive = False

    def draw(self, screen):
        pygame.draw.line(
            screen, "black", self.start_pos, self.end_pos, width=self.LINE_WIDTH
        )


class _RotatingRect:
    WIDTH = 3
    ROTAT_SPEED = 2.3

    def __init__(self, centerx, centery) -> None:
        self.size = random.randint(20, 40)

        self.rect = pygame.Rect((0, 0), (self.size, self.size))
        self.rect.center = centerx, centery
        self.original_rect = self.rect.copy()
        self.original_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(
            self.original_surf,
            "black",
            self.rect,
            # width=self.WIDTH
        )
        self.surf = self.original_surf.copy()
        self.angle = 0

    def update(self, dt):
        self.angle += self.ROTAT_SPEED * dt
        pygame.draw.rect(self.original_surf, "black", self.rect, width=self.WIDTH)
        self.surf = pygame.transform.rotate(self.original_surf, self.angle)
        self.rect = self.surf.get_rect(center=self.original_rect.center)

    def draw(self, screen):
        screen.blit(self.surf, self.rect)


class BackGroundEffect:
    N_LINES = 8
    LINE_PADDING = 40
    INIT_LINE = WIDTH

    def __init__(self) -> None:
        self.lines = [
            _Line((self.LINE_PADDING * i) - self.INIT_LINE) for i in range(self.N_LINES)
        ]
        self.rotating_rectangles = []
        self.rotat_rect_gen = Time(0.4)

    def update(self, event_info):
        dt = event_info["dt"]
        for index, line in enumerate(self.lines[:]):
            line.update()

            if not line.alive:
                self.lines[index] = _Line(-self.INIT_LINE)

        if self.rotat_rect_gen.update():
            self.rotating_rectangles.append(
                _RotatingRect(random.randrange(WIDTH), random.randrange(HEIGHT))
            )

        for rect in self.rotating_rectangles:
            rect.update(dt)

    def draw(self, screen):
        screen.fill(0xB2AC88)
        for rect in self.rotating_rectangles:
            rect.draw(screen)
        for line in self.lines:
            line.draw(screen)
