"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

from typing import Optional

import pygame

from game.common import HEIGHT, WIDTH, EventInfo
from game.states.enums import States
from library.sprite.load import load_assets
from library.transition import FadeTransition
from library.ui.buttons import Button


class InitDialogueStage:
    FRAME_COOLDOWN = 225

    def __init__(self, switch_info: dict):
        self.switch_info = switch_info

        self.assets = load_assets("intro")
        self.frames = [self.assets[f"frame_{n}"] for n in range(1, 4)]
        self.current_frame_index = 0
        self.frame_cooldown = self.FRAME_COOLDOWN

        self.switching = False

        self.transition = FadeTransition(True, self.FADE_SPEED, (WIDTH, HEIGHT))

        self.next_state: Optional[States] = None


class FrameDialogueStage(InitDialogueStage):
    def update(self, event_info: EventInfo):
        self.frame_cooldown -= event_info["dt"]
        if self.frame_cooldown < 0:
            self.switching = True
            self.frame_cooldown = self.FRAME_COOLDOWN

    def draw(self, screen: pygame.Surface):
        screen.blit(self.frames[self.current_frame_index], (0, 0))


class ButtonDialogueStage(FrameDialogueStage):
    def __init__(self, switch_info: dict):
        super().__init__(switch_info)

        self.skip_button = Button(
            pos=(WIDTH - 128, HEIGHT - 64),
            size=(128, 64),
            colors={"static": "grey", "hover": "white", "text": "black"},
            font_name="PixelMillenium",
            text="skip",
            corner_radius=8,
        )
        self.skip_button.rect

    def update(self, event_info: EventInfo):
        super().update(event_info)
        self.skip_button.update(event_info["mouse_pos"], event_info["mouse_press"])

        if self.skip_button.clicked:
            self.switching = True
            self.current_frame_index = len(self.frames) - 1

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        self.skip_button.draw(screen)


class TransitionDialogueStage(ButtonDialogueStage):
    FADE_SPEED = 4

    def update(self, event_info: EventInfo):
        super().update(event_info)
        self.transition.update(event_info["dt"])

        # if switching to the next frame
        if self.switching:
            # start fading in
            self.transition.fade_in = False
            # when finished fading in
            if self.transition.event:
                # fade out and increase the frame index
                self.current_frame_index += 1
                self.transition.fade_in = True
                self.switching = False

        if self.current_frame_index > len(self.frames) - 1:
            # just capping the index to avoid index error
            self.current_frame_index = len(self.frames) - 1
            # switching to the next state (made it level for debugging purposes)
            self.next_state = States.LEVEL

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        self.transition.draw(screen)


class Dialogue(TransitionDialogueStage):
    def update(self, event_info: EventInfo):
        super().update(event_info)

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
