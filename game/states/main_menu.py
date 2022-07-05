"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

from typing import Optional

import pygame

from game.common import HEIGHT, WIDTH, EventInfo
from game.states.enums import States
from library.sfx import SFXManager
from library.transition import FadeTransition


class InitMainMenuStage:
    def __init__(self, switch_info: dict) -> None:
        self.sfx_manager = SFXManager("main menu")
        self.switch_info = switch_info


class TransitionStage(InitMainMenuStage):
    """
    Handles game state transitions
    """

    FADE_SPEED = 2.4

    def __init__(self, switch_info: dict):
        super().__init__(switch_info)
        self.transition = FadeTransition(True, self.FADE_SPEED, (WIDTH, HEIGHT))
        self.next_state: Optional[States] = None

        # Store any information needed to be passed
        # on to the next state
        self.switch_info = {}

    def update(self, event_info: EventInfo):
        # super().update(event_info)
        """
        Update the transition stage

        Parameters:
            event_info: Information on the window events
        """
        self.transition.update(event_info["dt"])
        condition = False
        for event in event_info["events"]:
            if event.type == pygame.MOUSEBUTTONDOWN:
                condition = True

        if condition:
            self.transition.fade_in = False
            if self.transition.event:
                self.next_state = States.LEVEL

    def draw(self, screen: pygame.Surface) -> None:
        # super().draw(screen)
        self.transition.draw(screen)


class MainMenu(TransitionStage):
    pass
