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

        if isinstance(target_pos, tuple) or isinstance(target_pos, list):
            target_pos = pygame.Rect(target_pos[0], target_pos[1], 0, 0)
        elif isinstance(target_pos, pygame.Vector2):
            target_pos = pygame.Rect(target_pos.x, target_pos.y, 0, 0)

        return target_pos.move(self.camera.topleft)

    def adjust_to(self, target_pos: pygame.Vector2) -> None:
        """
        Adjusts the camera pos to the target pos

        Parameters:
            target_pos: the target position to adjust to
        """

        x = self.camera_width // 2 - target_pos.x
        y = self.camera_height // 2 - target_pos.y

        self.camera.topleft = (x, y)
        self.vec = (x, y)
