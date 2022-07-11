"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import math
import random
from typing import Tuple, Union

import pygame

from game.common import EventInfo
from library.utils.funcs import circle_surf, get_movement


class ParticleManager(set):
    def __init__(self, camera, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.camera = camera

    def update(self, event_info: EventInfo) -> None:
        dead_particles = set()

        for particle in self:
            particle.update(event_info["dt"])

            if not particle.alive:
                dead_particles.add(particle)

        self.difference_update(dead_particles)

    def draw(self) -> None:
        for particle in self:
            particle.draw(self.camera)


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
        color: Union[Tuple[int, int, int], str] = "white",
        lifespan: int = 0,
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
        self.lifespan = lifespan
        self.current_lifespan = 0
        self.alive = True

    def draw(self, camera):
        """
        Draws the particle on a pygame.Surface.
        """
        pygame.draw.circle(self.screen, self.color, camera.apply(self.pos), self.radius)

    def update(self, delta_time: float):
        """
        Updates the particle.
        """

        self.current_lifespan += 1

        # increase vel.y so particle goes down exponentially
        self.vel.y += self.gravity * delta_time

        # update particle position
        self.pos.x += self.vel.x * delta_time
        self.pos.y += self.vel.y * delta_time

        # decrease the radius
        self.radius -= self.radius_speed * delta_time

        if self.current_lifespan > self.lifespan or self.radius <= 0:
            self.alive = False


class MovingParticle:
    """
    Particle that moves in a specified direction
    (you can make it change its alpha (optional))
    """

    def __init__(
        self,
        screen: pygame.Surface,
        image: pygame.Surface,
        pos: Tuple[int],
        vel: Tuple[int],
        alpha_speed: int,
        starting_alpha: int = 255,
        lifespan: int = 0,
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
        self.lifespan = lifespan
        self.current_lifespan = 0
        self.alive = True

    def update(self, delta_time: float):
        """
        Updates the particle
        Parameters:
                scroll: World scroll
                delta_time: Time between frames
        """

        self.current_lifespan += 1

        self.pos.x += self.vel.x * delta_time
        self.pos.y += self.vel.y * delta_time

        self.alpha -= self.alpha_speed * delta_time
        self.image.set_alpha(self.alpha)

        if self.current_lifespan > self.lifespan or self.alpha == 0:
            self.alive = False

    def draw(self, camera):
        self.screen.blit(self.image, camera.apply(self.pos))


class TextParticle(MovingParticle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update(self, delta_time: float):
        self.vel.y *= 0.93

        super().update(delta_time)


class AngularParticle:
    def __init__(
        self,
        pos: Tuple[int, int],
        color: Union[Tuple[int, int, int], str],
        size: float,
        speed: float,
        shape: str,
        size_reduction,
        glow: bool = False,
        lifespan: int = 0,
        screen=None,
        angle=None,
    ):
        self.alive = True
        self.screen = screen

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

        self.lifespan = lifespan
        self.current_lifespan = 0

    def update(self, delta_time: float, speed_reduce=0):
        if speed_reduce:
            self.dx, self.dy = get_movement(self.angle, speed_reduce)
        self.vec[0] += self.dx * delta_time
        self.vec[1] += self.dy * delta_time

        # if self.size < 6:
        #     self.vec[1] += 120 * dt

        if self.current_lifespan > self.lifespan or self.size < 0:
            self.alive = False

        self.size -= self.size_reduction * delta_time
        self.rect = pygame.Rect(self.vec, (self.size, self.size))

    def draw(self, _=None, screen=None):
        if self.shape == "square":
            pygame.draw.rect(
                self.screen if self.screen is not None else screen,
                self.color,
                self.rect,
            )
        elif self.shape == "circle":
            pygame.draw.circle(
                self.screen if self.screen is not None else screen,
                self.color,
                self.rect.center,
                self.size,
            )

        if self.glow and self.size > 0:
            surf = circle_surf(self.size * 2, (20, 20, 20))
            r = surf.get_rect(center=self.rect.center)
            if self.screen is not None:
                self.screen.blit(surf, r, special_flags=pygame.BLEND_RGB_ADD)
            else:
                screen.blit(surf, r, special_flags=pygame.BLEND_RGB_ADD)
