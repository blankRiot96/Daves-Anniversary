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

    def __init__(self, image: pygame.Surface, pos: tuple[int, int]):
        """
        Parameters:
                image: Image of the tile
                pos: Position of the tile
        """
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, player):
        """
        Draws the tile
        Parameters:
                scroll: World camera scroll
        """


class SpikeTile:
    def __init__(self, img: pygame.Surface, obj):
        width = int(obj.width)
        height = int(obj.height)

        self.rect = pygame.Rect(int(obj.x), int(obj.y), width, height)
        self.surf = pygame.Surface((width, height))
        self.surf.set_colorkey("black")

        range_y = int(height / img.get_height())
        range_x = int(width / img.get_width())
        for y in range(range_y):
            for x in range(range_x):
                self.surf.blit(img, (x * img.get_width(), y * img.get_height()))

    def update(self, player):
        if player.rect.colliderect(self.rect):
            player.alive = False

    def draw(self, screen: pygame.Surface, camera):
        screen.blit(self.surf, camera.apply(self.rect))


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
