"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

from typing import Sequence

import pygame

from library.common import Pos
from library.utils import Expansion


class Animation:
    def __init__(
        self,
        frames: Sequence[pygame.surface.Surface],
        speed: float,
        reversive: bool = False,
    ):
        self.frames = frames
        self.speed = speed
        self.reversive = reversive

        self.f_len = len(frames)

        self.expansion = Expansion(0, 0, self.f_len, self.speed) if reversive else None

        self.index = 0
        self.animated_once = False

    def _check_size(self):
        if self.index >= self.f_len:
            self.index = 0
            self.animated_once = True

    def normal_update(self, dt: float):
        self.index += self.speed * dt

    def reversive_update(self, dt: float):
        self.expansion.update_auto(dt)
        self.index = self.expansion.number

    def update(self, dt):
        if self.reversive:
            self.reversive_update(dt)
        else:
            self.normal_update(dt)

        self._check_size()

    def draw(self, screen: pygame.Surface, pos: Pos, blit_by: str = "topleft"):
        frame = self.frames[int(self.index)]

        if blit_by:
            frame_rect = frame.get_rect()
            setattr(frame_rect, blit_by, tuple(pos))
            pos = frame_rect.topleft

        screen.blit(frame, pos)

    def play(self, screen, pos, dt, blit_by: str = "topleft"):
        self.update(dt)
        self.draw(screen, pos, blit_by)
