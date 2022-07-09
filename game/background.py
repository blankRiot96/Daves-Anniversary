"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import logging
import math
import random

import pygame

from game.common import HEIGHT, WIDTH
from game.states.enums import Dimensions
from library.particles import AngularParticle
from library.ui.camera import Camera
from library.utils.classes import Time

logger = logging.getLogger()


_BACKGROUND_COLORS = {
    Dimensions.PARALLEL_DIMENSION: (25, 22, 20),
    Dimensions.ALIEN_DIMENSION: (14, 13, 20),
    Dimensions.VOLCANIC_DIMENSION: (19, 16, 15),
}


class _Line:
    LINE_WIDTH = 7
    SPEED = 1.3
    _n_instanced = 0

    def __init__(self) -> None:
        # self.start_pos = pygame.Vector2(0, (self._n_instanced * padding) * (HEIGHT / WIDTH))
        # self.end_pos = pygame.Vector2(self._n_instanced * padding, 0)
        self.start_pos = pygame.Vector2((0, 0))
        self.end_pos = pygame.Vector2((0, 0))
        self.alive = True
        self.distance_travelled = 0
        self.diagonal_distance = math.sqrt((WIDTH**2) + (HEIGHT**2))

        # Incrementing counter for every time
        # a line is instanced
        type(self)._n_instanced += 1

    def update(self, dt):
        domino = False
        if self.start_pos.y < HEIGHT:
            domino = True
            self.start_pos.y += self.SPEED * dt * (HEIGHT / WIDTH)
        else:
            self.start_pos.x += self.SPEED * dt

        if self.end_pos.x < WIDTH:
            self.end_pos.x += self.SPEED * dt
        else:
            self.end_pos.y += (self.SPEED * dt) * (HEIGHT / WIDTH)

        if not domino and self.start_pos.x >= WIDTH and self.start_pos.y >= HEIGHT:
            self.alive = False

    def draw(self, screen):
        pygame.draw.line(
            screen, (6, 6, 8), self.start_pos, self.end_pos, width=self.LINE_WIDTH
        )


class _RotatingRect:
    WIDTH = 3
    ROTAT_SPEED = 0.3
    SPEED = 0.4

    def __init__(self, rotat_img) -> None:
        self.size = random.randint(20, 40)
        self.size = (self.size, self.size)
        self.SPEED = self.SPEED * (self.size[0] / 40)
        self.alive = True
        self.rect = pygame.Rect((0, 0), self.size)
        self.rect.center = random.randrange(-WIDTH, WIDTH * 3), HEIGHT
        self.original_rect = self.rect.copy()
        self.original_surf = pygame.transform.scale(rotat_img.copy(), self.size)
        # pygame.draw.rect(
        #     self.original_surf,
        #     "blue",
        #     self.rect,
        #     width=self.WIDTH
        # )
        self.surf = rotat_img.copy()
        self.angle = 0
        self.vec = pygame.Vector2(self.rect.center)

        self.particles: set[AngularParticle] = set()
        self.particle_gen_time = Time(0.1)

    def handle_contrail(self, dt):
        if self.particle_gen_time.update():
            self.particles.add(
                AngularParticle(
                    self.vec - (random.uniform(-self.size[0] / 2, self.size[0] / 2), 0),
                    (179, 185, 209),
                    3,
                    0.3,
                    "square",
                    0.03,
                    glow=True,
                    angle=math.radians(90),
                )
            )

        for particle in set(self.particles):
            particle.update(dt)

            if particle.size <= 0.1:
                self.particles.remove(particle)

    def update(self, dt):
        self.angle += self.ROTAT_SPEED * dt
        pygame.draw.rect(self.original_surf, (6, 6, 8), self.rect, width=self.WIDTH)
        self.surf = pygame.transform.rotate(self.original_surf, self.angle)
        self.rect = self.surf.get_rect(center=self.original_rect.center)

        self.vec.y -= self.SPEED * dt
        self.rect.center = self.vec

        if self.vec.y < -100:
            self.alive = False

        # self.handle_contrail(dt)

    def draw(self, screen, camera: Camera):
        for particle in self.particles:
            particle.draw(screen)
        screen.blit(self.surf, self.rect.topleft + pygame.Vector2(camera.vec))


class BackGroundEffect:
    N_LINES = 13
    LINE_PADDING = 300
    INIT_LINE = WIDTH

    def __init__(self, assets) -> None:
        self.lines = []
        self.line_gen = Time(1)
        self.rotating_rectangles = []
        self.rotat_rect_gen = Time(0.3)
        self.assets = assets

    def update(self, event_info):
        dt = event_info["dt"]

        for line in self.lines:
            line.update(dt)

            if not line.alive:
                self.lines.remove(line)

        if self.line_gen.update():
            self.lines.append(_Line())

        for rect in self.rotating_rectangles:
            rect.update(dt)

            if not rect.alive:
                self.rotating_rectangles.remove(rect)

        if self.rotat_rect_gen.update():
            self.rotating_rectangles.append(_RotatingRect(self.assets["rotating_rect"]))

    def draw(self, screen, camera, current_dimension):
        screen.fill(_BACKGROUND_COLORS[current_dimension])

        for rect in self.rotating_rectangles:
            rect.draw(screen, camera)

        for line in self.lines:
            line.draw(screen)
