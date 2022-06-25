"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import pygame

from library.sfx import SFXManager as _SFXManager
from library.ui.slider import HorizontalSlider


class SoundIcon:
    SIZE = 32, 32

    def __init__(self, sfx_manager: _SFXManager, assets, center_pos):
        self.sfx_manager = sfx_manager

        slider_rect = pygame.Rect(50, 180, 110, 30)
        slider_rect.center = center_pos + pygame.Vector2(0, 30)
        self.on_img = pygame.transform.scale(assets["sound_icon_on"], self.SIZE)
        self.off_img = pygame.transform.scale(assets["sound_icon_off"], self.SIZE)
        self.switch = True
        self.img = self.on_img
        self.vec = pygame.Vector2(center_pos)
        self.rect = self.img.get_rect(center=center_pos)
        self.last_percent = 100

        self.larger_rect = pygame.Rect(
            (0, 0),
            (
                slider_rect.width + self.rect.width,
                slider_rect.height + self.rect.height + 30,
            ),
        )
        self.larger_rect.center = center_pos

        def handle_callback(value: int):
            given_value = value * 4
            total_value = slider_rect.width
            percentage = (given_value / total_value) * 100
            self.last_percent = percentage
            self.sfx_manager.set_volume(percentage)

        self.slider = HorizontalSlider(slider_rect, step=1, callback=handle_callback)
        self._handle_slider = True

    def update(self, event_info):
        self._handle_slider = self.switch and self.larger_rect.collidepoint(
            event_info["mouse_pos"]
        )
        if self._handle_slider:
            self.slider.update(event_info["events"])

        for event in event_info["events"]:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.switch = not self.switch

                    if self.switch:
                        self.img = self.on_img
                        self.sfx_manager.set_volume(self.last_percent)
                    else:
                        self.img = self.off_img
                        self.sfx_manager.set_volume(0)

    def draw(self, screen):
        if self._handle_slider:
            self.slider.draw(screen)
        screen.blit(self.img, self.rect)
