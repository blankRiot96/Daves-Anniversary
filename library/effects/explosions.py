
"""
An explosion, is essentially just a way to 
handle particles going in all directions with 
different sizes and speeds
This causes a nice explosion based effect

You can also specify an angle of the explosion to
explode around that place, explosions are great
"""


import random
import pygame
from library.particles import AngularParticle
from library.common import Pos
from typing import List, Set


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

    def draw(self, screen, dt):
        for particle in self.particles:
            particle.draw(screen, dt)

            if particle.size < 0:
                self.particles.remove(particle)


class ExplosionManager:
    EXP_TYPES = {
        "arcade": {
            "n_particles": 500,
            "n_size": (3, 10),
            "speed": (0.09, 1.3),
            "shape": "square",
            "color": "rainbow",
            "glow": False,
            "size_reduction": 0.2
        },
    }

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

    def update(self):
        for explosion in set(self.explosions):
            if len(explosion.particles) == 0:
                self.explosions.remove(explosion)

    def draw(self, screen: pygame.Surface, dt: float):
        for explosion in self.explosions:
            explosion.draw(screen, dt)
