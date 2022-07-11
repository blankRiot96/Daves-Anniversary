"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

from typing import Optional

import pygame

import library.utils
from game.common import HEIGHT, WIDTH, EventInfo
from game.states.enums import States
from library.sfx import SFXManager
from library.transition import FadeTransition
from library.ui.buttons import Button


class InitMainMenuStage:
    def __init__(self, switch_info: dict) -> None:
        self.sfx_manager = SFXManager("main_menu")
        self.switch_info = switch_info
        self._change_dim = False
        self._next_state = None


class RenderBackgroundStage(InitMainMenuStage):
    def draw(self, screen):
        screen.fill((23, 9, 14))


class UIStage(RenderBackgroundStage):
    """
    Handles buttons
    """

    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)

        texts = ("start", "intro", "reset", "credits")
        button_pad_y = 20
        self.buttons = tuple(
            (
                Button(
                    pos=(50, ((30 + button_pad_y) * index) + 50),
                    size=(120, 30),
                    colors={
                        "static": (14, 13, 20),
                        "hover": (25, 20, 32),
                        "text": (85, 87, 91),
                    },
                    font_name=None,
                    text=text,
                    corner_radius=3,
                )
                for index, text in enumerate(texts)
            )
        )
        self.font_surf = library.utils.font(size=50, name=None).render(
            "Dave's Anniversary", True, (72, 74, 98)
        )

    def update(self, event_info: EventInfo):
        """
        Update the Button state

        Parameters:
            event_info: Information on the window events
        """
        for button in self.buttons:
            button.update(event_info["mouse_pos"], event_info["mouse_press"])

            if button.clicked:
                if button.text == "start":
                    self._change_dim = True
                    self._next_state = States.LEVEL
                elif button.text == "intro":
                    self._change_dim = True
                    self._next_state = States.DIALOGUE

    def draw(self, screen: pygame.Surface):
        """
        Draw the Button state

        Parameters:
            screen: pygame.Surface to draw on
        """
        super().draw(screen)
        for button in self.buttons:
            button.draw(screen)

        screen.blit(
            self.font_surf,
            (200, screen.get_rect().centery - self.font_surf.get_height()),
        )


class TransitionStage(UIStage):
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
        super().update(event_info)
        """
        Update the transition stage

        Parameters:
            event_info: Information on the window events
        """
        self.transition.update(event_info["dt"])
        if self._change_dim:
            self.transition.fade_in = False
            if self.transition.event:
                self.next_state = self._next_state

    def draw(self, screen: pygame.Surface) -> None:
        super().draw(screen)
        self.transition.draw(screen)


class MainMenu(TransitionStage):
    pass
