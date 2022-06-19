"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""


import pygame
from game.common import EventInfo


# TODO: Make Player a pygame.sprite.Sprite
class Player:
    """
    Handles player
    """

    SIZE = (20, 20)
    SPEED = 1.2

    def __init__(self):
        self.alive = True
        self.image = pygame.Surface(self.SIZE)
        self.image.fill("red")
        self.rect = pygame.Rect((0, 0), self.SIZE)
        self.x, self.y = 0, 0
        self.vec = pygame.Vector2()

    def change_coord(self, dx: float, dy: float):
        """
        Changes all the relevant coordinates of the 
        player 
        """
        self.vec += dx, dy
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)


    def update(self, event_info: EventInfo) -> None:
        """
        Updates the player class
        Handles key input

        Parameters:
            event_info: Information on the window events
        """

        dx, dy = 0, 0

        dt = event_info["dt"]
        keys = event_info["key_press"]
        if keys[pygame.K_d]:
            dx += self.SPEED * dt
        if keys[pygame.K_a]:
            dx -= self.SPEED * dt
        if keys[pygame.K_w]:
            dy -= self.SPEED * dt
        if keys[pygame.K_s]:
            dy += self.SPEED * dt

        self.change_coord(dx, dy)

    def draw(self, screen: pygame.Surface):
        """
        Draws the player

        Parameters:
            screen: pygame.Surface to draw player on
        """
        screen.blit(self.image, self.vec)
