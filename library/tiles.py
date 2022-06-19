"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import pygame

from library.utils import Animation


class Tile:
    """
    Collidable tile
    """

    def __init__(self, screen: pygame.Surface, image: pygame.Surface, pos: tuple[int]):
        """
        Parameters:
                screen: Surface on which the tile is drawn
                image: Image of the tile
                pos: Position of the tile
        """
        self.screen = screen
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, scroll: pygame.Vector2):
        """
        Draws the tile
        Parameters:
                scroll: World camera scroll
        """
        self.screen.blit(self.image, self.rect.topleft - scroll)


class AnimatedDecorationTile:
    """
    Uncollidable animated tile
    """

    def __init__(
        self,
        screen: pygame.Surface,
        animation: Animation,
        animation_speed: float,
        pos: tuple[int],
    ):
        """
        Parameters:
                screen: Surface on which the tile is drawn
                animation: Animation of the tile
                animation_speed: Animation speed of the tile
                pos: Position of the tile
        """
        self.screen = screen
        self.animation = animation
        self.animation_speed = animation_speed
        self.pos = pos

    def update(self, scroll: pygame.Vector2, delta_time: float):
        """
        Updates the tile
        Parameters:
                scroll: World camera scroll
                delta_time: Time between frames
        """
        self.animation.play(
            self.screen, self.pos - scroll, self.animation_speed, delta_time
        )
