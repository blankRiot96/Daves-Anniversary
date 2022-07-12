"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.

An explosion, is essentially just a way to 
handle particles going in all directions with 
different sizes and speeds
This causes a nice explosion based effect

You can also specify an angle of the explosion to
explode around that place, explosions are great
"""


import json
import random
from typing import List, Set

import pygame

from game.common import DATA_DIR
from library.common import Pos
from library.particles import AngularParticle


class Explosion:
    def __init__(
        self,
        n_particles,
        n_size,
        pos,
        speed,
        color,
        size_reduction=5,
        glow=True,
    ):
        self.n_particles = n_particles
        self.n_size = n_size

        if color == "rainbow":
            get_color = lambda: tuple((random.randrange(255) for _ in range(3)))
        else:
            get_color = lambda: color
        self.particles: List[AngularParticle] = [
            AngularParticle(
                pos=pos,
                color=get_color(),
                size=random.randrange(*n_size),
                speed=random.uniform(*speed),
                shape="square",
                glow=glow,
                size_reduction=size_reduction,
            )
            for _ in range(n_particles)
        ]

    def update(self, dt):
        for particle in self.particles:
            particle.update(dt)

            if particle.size < 0:
                self.particles.remove(particle)

    def draw(self, screen, camera=(0, 0)):
        for particle in self.particles:
            particle.draw(screen=screen)


class ExplosionManager:
    with open(DATA_DIR / "explosion.json") as f:
        EXP_TYPES = json.load(f)

    def __init__(self, exp_type: str):
        self.exp_type: str = exp_type
        self.explosions: Set[Explosion] = set()

    def create_explosion(self, pos: Pos):
        data = self.EXP_TYPES[self.exp_type]
        self.explosions.add(
            Explosion(
                n_particles=data["n_particles"],
                n_size=data["n_size"],
                pos=pos,
                speed=data["speed"],
                color=data["color"],
                glow=data["glow"],
                size_reduction=data["size_reduction"],
            )
        )

    def update(self, dt: float):
        for explosion in set(self.explosions):
            explosion.update(dt)

            if len(explosion.particles) == 0:
                self.explosions.remove(explosion)

    def draw(self, screen: pygame.Surface):
        for explosion in self.explosions:
            explosion.draw(screen)
