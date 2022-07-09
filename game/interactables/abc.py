"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import abc

import pygame

from library.common import Pos
from library.ui.camera import Camera


class Interactable(abc.ABC):
    """
    A base interactable class which switches images
    if the player is interacting with it
    """

    def __init__(
        self,
        non_interacting_img: pygame.Surface,
        interacting_img: pygame.Surface,
        pos: Pos,
    ) -> None:
        """
        Parameters:
            non_interacting_img: Surface to draw when player not interacting with interactable
            interacting_img: Surface to draw when player is interacting with interactable
            pos: Position to draw at
        """

        self.non_interacting_img = non_interacting_img
        self.interacting_img = interacting_img
        self.img = non_interacting_img
        self.rect = self.img.get_rect(topleft=pos)
        self.interacting = False

    def update(self, player_rect: pygame.Rect):
        self.img = self.non_interacting_img
        self.interacting = self.rect.colliderect(player_rect)
        if self.interacting:
            self.img = self.interacting_img

    def draw(self, screen: pygame.Surface, camera: Camera):
        screen.blit(self.img, camera.apply(self.rect))
