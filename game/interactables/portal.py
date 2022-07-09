"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import itertools
from typing import List

import pygame

from game.interactables.abc import Interactable
from game.states.enums import Dimensions


class Portal(Interactable):
    def __init__(self, obj, dimensions: List[Dimensions], imgs: list[pygame.Surface]):
        super().__init__(imgs[0], imgs[1], (obj.x, obj.y))
        self.dimension_cycle = itertools.cycle(dimensions)
        self.current_dimension = next(self.dimension_cycle)
        self.dimension_change = False

    def update(self, player_rect, events):
        super().update(player_rect)
        self.dimension_change = False
        self.events = events

        # if the player is standing next to the portal
        if self.interacting:
            for event in events["events"]:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        # switch to the next dimension
                        self.dimension_change = True
                        self.current_dimension = next(self.dimension_cycle)
