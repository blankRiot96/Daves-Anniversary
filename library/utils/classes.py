"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.

This file is a part of the 'ecs-pygame' source code.
The source code is distributed under the MIT license.
"""

import time

import pygame


class Glow:
    def __init__(self, image: pygame.Surface, color, topleft):
        self.img_rect = image.get_bounding_rect()
        self.img_rect.topleft = topleft
        self.surf = circle_surf(self.img_rect.height, color)
        self.rect = self.surf.get_rect(center=self.img_rect.center)

    def change_pos(self, new_pos):
        self.rect = pygame.Rect(new_pos, self.rect.size)

    def draw(self, screen: pygame.Surface, camera):
        screen.blit(
            self.surf,
            (
                self.rect.x - camera[0],
                self.rect.y - camera[1] + (self.img_rect.height // 2),
            ),
            special_flags=pygame.BLEND_RGB_ADD,
        )


class Time:
    """
    Class to check if time has passed.
    """

    def __init__(self, time_to_pass: float):
        self.time_to_pass = time_to_pass
        self.start = time.perf_counter()

    def update(self) -> bool:
        if time.perf_counter() - self.start > self.time_to_pass:
            self.start = time.perf_counter()
            return True
        return False


class Expansion:
    """
    Number expansion and contraption
    """

    def __init__(
        self,
        number: float,
        lower_limit: float,
        upper_limit: float,
        speed: float,
    ):
        self.number = number
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.speed = speed
        self.auto_cond = True

    def update_auto(self, dt: float):
        if self.auto_cond:
            if self.number < self.upper_limit:
                self.number += self.speed * dt
            else:
                self.auto_cond = False
        else:
            if self.number > self.lower_limit:
                self.number -= self.speed * dt
            else:
                self.auto_cond = True

    def update(self, cond: bool, dt: float):
        if cond:
            if self.number < self.upper_limit:
                self.number += self.speed * dt
        else:
            if self.number > self.lower_limit:
                self.number -= self.speed * dt
