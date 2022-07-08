"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

from typing import Callable, Optional

import pygame


class FadeTransition:
    def __init__(self, fade_in: bool, fade_speed: float, size: tuple[int, int]):
        self.fade_in = fade_in
        self.init_fade = fade_in
        self.fade_speed = fade_speed
        self.image = pygame.Surface(size)

        self.event = False
        self.alpha = 255 if fade_in else 0
        self.image.set_alpha(self.alpha)
        self.effects = []

    def _handle_fade_in(self, dt: float):
        if self.alpha > 0:
            self.alpha -= self.fade_speed * dt
            self.event = False
        else:
            self.alpha = 0
            if not self.init_fade:
                self.event = True

    def _handle_fade_out(self, dt: float):
        if self.alpha < 255:
            self.alpha += self.fade_speed * dt
            self.event = False
        else:
            self.alpha = 255
            if self.init_fade:
                self.event = True
    
    def fade_out_in(self, on_finish: Optional[Callable] = None):
        def func(self):
            self.fade_in = False
            if self.event and not self.fade_in:
                self.fade_in = True

                if on_finish is not None:
                    on_finish()

                self.effects.remove(func)

        self.effects.append(func)


    def update(self, dt: float) -> None:
        for effect in self.effects:
            effect(self)

        if self.fade_in:
            self._handle_fade_in(dt)
        else:
            self._handle_fade_out(dt)

        self.image.set_alpha(int(self.alpha))

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, (0, 0))
