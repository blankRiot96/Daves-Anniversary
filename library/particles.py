"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import pygame
import math
import random

from library.utils.funcs import get_movement, circle_surf


class Particle:
    """
    Customizable particle class.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        pos: tuple[int],
        radius: int = 5,
        radius_speed: int = 0.075,
        vel: tuple[int] = (-0.5, 0.1),
        gravity: float = 0.1,
        color: tuple[int] | str = "white",
    ):
        """
        Parameters:
            pos: Position of the particle
            radius: Radius of the particle
            radius_speed: Decreasing speed of the particle's radius
            vel: How far does the particle move (x, y)
            gravity: Fall speed of the particle
        """
        self.screen = screen
        self.pos = pygame.Vector2(pos)
        self.radius = radius
        self.radius_speed = radius_speed
        self.vel = pygame.Vector2(vel)
        # flip the y velocity so the particle goes up and then fall
        self.vel.y = -self.vel.y
        self.gravity = gravity
        self.color = color

    def draw(self, scroll: pygame.Vector2):
        """
        Draws the particle on a pygame.Surface.
        """
        pygame.draw.circle(self.screen, self.color, self.pos - scroll, self.radius)

    def update(self, scroll: pygame.Vector2, delta_time: float):
        """
        Updates the particle.
        """

        # increase vel.y so particle goes down exponentially
        self.vel.y += self.gravity * delta_time

        # update particle position
        self.pos.x += self.vel.x * delta_time
        self.pos.y += self.vel.y * delta_time

        # decrease the radius
        self.radius -= self.radius_speed * delta_time

        # draw the particle
        self.draw(scroll)


class MovingParticle:
    """
    Particle that moves in a specified direction
    (you can make it change its alpha (optional))
    """

    def __init__(
        self,
        screen: pygame.Surface,
        image: pygame.Surface,
        pos: tuple[int],
        vel: tuple[int],
        alpha_speed: int,
        starting_alpha: int = 255,
    ):
        """
        Parameters:
                screen: Display surface
                image: Particles's surface
                pos: Starting position
                vel: Velocity of the particle (added to its position every frame)
                alpha_speed: Alpha speed (it's added to the image's alpha every frame)
                starting_alpha: Starting alpha
        """
        self.screen = screen
        self.image = image
        self.alpha = starting_alpha
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.alpha_speed = alpha_speed

    def update(self, scroll: pygame.Vector2, delta_time: float):
        """
        Updates the particle
        Parameters:
                scroll: World scroll
                delta_time: Time between frames
        """
        self.pos.x += self.vel.x * delta_time
        self.pos.y += self.vel.y * delta_time

        self.alpha -= self.alpha_speed * delta_time
        self.image.set_alpha(self.alpha)

        self.screen.blit(self.image, self.pos - scroll)


class AngularParticle:
    def __init__(
        self,
        pos,
        color,
        size,
        speed,
        shape: str,
        size_reduction,
        glow: bool = False,
        angle=None,
    ):
        self.pos = pos
        self.color = color
        self.size = size
        self.speed = speed
        self.shape = shape
        self.vec = pygame.Vector2(self.pos)
        # self.vec.rotate(random.randrange(0, 360))
        if angle is None:
            self.angle = math.atan2(
                random.randrange(-300, 500) - random.randrange(-300, 500),
                random.randrange(-300, 500) - random.randrange(-300, 500),
            )
        else:
            self.angle = angle
        self.dx, self.dy = get_movement(self.angle, speed)

        self.rect = pygame.Rect(tuple(self.pos), (size, size))
        self.size_reduction = size_reduction
        self.glow = glow

    def draw(self, screen, dt, speed_reduce=0):
        if speed_reduce:
            self.dx, self.dy = get_movement(self.angle, speed_reduce)
        self.vec[0] += self.dx * dt
        self.vec[1] += self.dy * dt

        # if self.size < 6:
        #     self.vec[1] += 120 * dt

        self.size -= self.size_reduction * dt
        self.rect = pygame.Rect(self.vec, (self.size, self.size))

        if self.shape == "square":
            pygame.draw.rect(screen, self.color, self.rect)
        elif self.shape == "circle":
            pygame.draw.circle(screen, self.color, self.rect.center, self.size)

        if self.glow and self.size > 0:
            surf = circle_surf(self.size * 2, (20, 20, 20))
            r = surf.get_rect(center=self.rect.center)
            screen.blit(surf, r, special_flags=pygame.BLEND_RGB_ADD)
