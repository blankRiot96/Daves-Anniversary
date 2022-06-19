"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import abc
from typing import Optional

import pygame

from game.common import EventInfo
from game.player import Player
from game.states.enums import States
from library.transition import FadeTransition


class InitLevelStage(abc.ABC):
    def __init__(self) -> None:
        """
        Initialize some attributes
        """


class PlayerStage(InitLevelStage):
    """
    Handle player related actions
    """

    def __init__(self):
        super().__init__()
        self.player = Player()

    def update(self, event_info: EventInfo):
        self.player.update(event_info)

    def draw(self, screen: pygame.Surface):
        self.player.draw(screen)


class TransitionStage(PlayerStage):
    """
    Handles game state transitions
    """

    FADE_SPEED = 4

    def __init__(self):
        super().__init__()
        self.transition = FadeTransition(True, self.FADE_SPEED, (420, 200))
        self.next_state: Optional[States] = None

        # Store any information needed to be passed
        # on to the next state
        self.switch_info = {}

    def update(self, event_info: EventInfo):
        super().update(event_info)
        """
        Update the transition stage

        Parameters:
            event_info: Information on the window events
        """
        self.transition.update(event_info["dt"])
        if not self.player.alive:
            self.transition.fade_in = False
            if self.transition.event:
                self.next_state = States.MAIN_MENU

    def draw(self, screen: pygame.Surface) -> None:
        super().draw(screen)
        self.transition.draw(screen)


class Level(TransitionStage):
    """
    Final element of stages chain
    """

    def update(self, event_info: EventInfo):
        """
        Update the Level state

        Parameters:
            event_info: Information on the window events
        """
        super().update(event_info)

    def draw(self, screen: pygame.Surface):
        """
        Draw the Level state

        Parameters:
            screen: pygame.Surface to draw on
        """
        super().draw(screen)