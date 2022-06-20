"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.

File containing a bunch of surface manipulation
based utility
"""

import pygame


class FadingImage:
    """
    Image that can fade in and/or fade out
    """

    FADE_OUT_DURATION_DIVISOR = 15

    def __init__(
        self,
        image: pygame.Surface,
        speed: int,
        duration: int,
        pos: tuple[int],
        screen: pygame.Surface,
        starting_alpha: int = 0,
        fading_in: bool = True,
    ):

        self.image = image
        self.speed = speed
        self.pos = pos
        self.duration = duration
        self.screen = screen
        self.alpha = starting_alpha
        self.fading_in = fading_in
        self.finished = False

    def fade_in(self, delta_time: float = 1):
        """
        Makes the image fade in

        Parameters:
                delta_time: Time between frames (optional)
        """
        self.alpha += self.speed * delta_time
        # if the image should fade out
        if self.alpha >= 255 + self.duration:
            self.fading_in = False

    def fade_out(self, delta_time: float = 1):
        """
        Makes the image fade out

        Parameters:
                delta_time: Time between frames (optional)
        """
        self.alpha -= self.speed * delta_time

        # self.finished = True if the animation is finished
        # (duration is decreased when fading out)
        if self.alpha <= 0 - self.duration / self.FADE_OUT_DURATION_DIVISOR:
            self.finished = True
            self.fading_in = True

    def update(self, delta_time: float = 1):
        """
        Updates, fades in/out, draws the image

        Parameters:
                delta_time: Time between frames (optional)
        """
        if self.fading_in:
            self.fade_in(delta_time)
        else:
            self.fade_out(delta_time)

        self.image.set_alpha(self.alpha)

        self.screen.blit(self.image, self.pos)


class Background:
    """
    Parralax background class
    """

    def __init__(
        self,
        screen: pygame.Surface,
        #             layer           speed
        layers: list[(pygame.Surface, float)],
    ):

        self.screen = screen
        self.width = screen.get_width()
        self.layers = layers

    def draw_layer(self, layer: pygame.Surface, scroll: pygame.Vector2, speed: float):
        """
        Draws a layer of the background on the screen

        Parameters:
                layer: Image of the layer
                scroll: World scroll
                speed: Moving speed of the layer
        """
        x = -scroll.x * speed

        x %= self.width

        if abs(x) <= self.width:
            self.screen.blit(layer, (x, 0))
        if x != 0:
            self.screen.blit(layer, (x - self.width, 0))

    def update(self, world_scroll: pygame.Vector2):
        """
        Updates and draws all layers of the background

        Parameters:
                world_scroll: World camera scroll
        """
        for layer, speed in self.layers:
            self.draw_layer(layer, world_scroll, speed)
