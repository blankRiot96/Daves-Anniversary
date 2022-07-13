import pygame
from game.common import SAVE_DATA
from game.interactables.abc import Interactable
from game.utils import load_font
from library.common import Pos
from library.particles import TextParticle


class Ring(Interactable):
    def __init__(self, ring_img, pos: Pos, particle_manager) -> None:
        super().__init__(ring_img, ring_img, pos)

        self.on_ground = True
        self.particle_manager = particle_manager
        self.screen = None
        
    def update(self, player_rect, player):
        if self.on_ground:
            super().update(player_rect)

            if self.rect.colliderect(player_rect):
                self.on_ground = False
                player.has_ring = True

                if self.screen is not None:
                    self.particle_manager.add(
                        TextParticle(
                            screen=self.screen,
                            image=load_font(16).render(
                                "Grabbed ring", True, (255, 255, 255)
                            ),
                            pos=player_rect.topleft,
                            vel=(0, -2),
                            alpha_speed=3,
                            lifespan=100,
                        )
                    )

                SAVE_DATA["has_ring"] = True
        
    def draw(self, screen, camera):
        self.screen = screen
        if self.on_ground:
            super().draw(screen, camera)