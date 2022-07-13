"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

from typing import Union

import pygame


class Camera:
    """
    Handles camera movement.
    The main advantage of this class over a simple Vector2 is ease of use
    """

    def __init__(self, camera_width: int, camera_height: int):
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.camera = pygame.Rect(0, 0, self.camera_width, self.camera_height)
        self.vec = pygame.Vector2(0, 0)

    def apply(
        self, target_pos: Union[pygame.Rect, pygame.Vector2, tuple, list]
    ) -> pygame.Rect:
        """
        Adjusts the target pos to the current camera pos

        Parameters:
            target_pos: the target position to adjust
        """
        target_pos = pygame.Rect(target_pos[0], target_pos[1], 0, 0)

        return target_pos.move((-self.camera.x, -self.camera.y))
    
    def hard_apply(
        self, target_pos: Union[pygame.Rect, pygame.Vector2, tuple, list]
    ) -> pygame.Rect:
        target_pos = pygame.Rect(target_pos[0], target_pos[1], 0, 0)

        return target_pos.move(self.camera.topleft)

    def adjust_to(self, dt: float, target_pos: pygame.Vector2) -> None:
        """
        Smoothly adjusts the camera pos to the target pos

        Parameters:
            dt: deltatime
            target_pos: the target position to adjust to
        """

        self.camera.x += (
            dt * (target_pos.x - self.camera.x - self.camera_width // 2) // 26
        )

        self.camera.y += (
            dt * (target_pos.y - self.camera.y - self.camera_height // 2) // 26
        )
    
    def hard_adjust_to(self, target_pos: pygame.Vector2) -> None:
        x = self.camera_width // 2 - target_pos.x
        y = self.camera_height // 2 - target_pos.y

        self.camera.topleft = (x, y)
