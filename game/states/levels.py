"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import abc
from asyncio.log import logger
from typing import Optional

import pygame

from game.common import HEIGHT, MAP_DIR, WIDTH, EventInfo
from game.player import Player
from game.sound_icon import SoundIcon
from game.states.enums import States
from library.effects import ExplosionManager
from library.sfx import SFXManager
from library.sprite.load import load_assets
from library.tilemap import TileLayerMap
from library.transition import FadeTransition
from library.ui.buttons import Button
from library.ui.camera import Camera


class InitLevelStage(abc.ABC):
    def __init__(self, switch_info: dict) -> None:
        self.switch_info = switch_info
        """
        Initialize some attributes
        """
        self.camera = Camera(WIDTH, HEIGHT)
        self.sfx_manager = SFXManager("level")
        self.assets = load_assets("level")
        self.event_info = {}


class TileStage(InitLevelStage):
    """
    Handles tilemap rendering
    """

    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)
        self.tilemap = TileLayerMap(MAP_DIR / "dimension_one.tmx")

        self.map_surf = self.tilemap.make_map()

    def draw(self, screen: pygame.Surface):
        screen.blit(self.map_surf, self.camera.apply((0, 0)))


class PlayerStage(TileStage):
    """
    Handle player related actions
    """

    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)
        self.player = Player()

    def update(self, event_info: EventInfo):
        self.player.update(event_info, self.tilemap)
        self.event_info = event_info

        # Temporary checking here 
        if self.player.y > 2000:
            self.player.alive = False

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        self.player.draw(screen, self.camera)


class CameraStage(PlayerStage):
    def update(self, event_info: EventInfo):
        super().update(event_info)
        self.camera.adjust_to(self.player.rect)


class UIStage(CameraStage):  # Skipped for now
    """
    Handles buttons
    """

    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)
        self.buttons = ()

        self.sound_icon = SoundIcon(self.sfx_manager, self.assets, center_pos=(700, 30))

    def update(self, event_info: EventInfo):
        """
        Update the Button state

        Parameters:
            event_info: Information on the window events
        """
        super().update(event_info)
        for button in self.buttons:
            button.update(event_info["mouse_pos"], event_info["mouse_press"])

        self.sound_icon.update(event_info)

    def draw(self, screen: pygame.Surface):
        """
        Draw the Button state

        Parameters:
            screen: pygame.Surface to draw on
        """
        super().draw(screen)
        for button in self.buttons:
            button.draw(screen)
        self.sound_icon.draw(screen)


class ExplosionStage(UIStage):  # Skipped for now
    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)
        self.explosion_manager = ExplosionManager("fire")

    def update(self, event_info: EventInfo) -> None:
        super().update(event_info)
        self.explosion_manager.update()

        for event in event_info["events"]:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.explosion_manager.create_explosion(event.pos)
                self.sfx_manager.play("explosion")

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        self.explosion_manager.draw(screen, self.event_info["dt"])


class TransitionStage(ExplosionStage):
    """
    Handles game state transitions
    """

    FADE_SPEED = 4
    
    def __init__(self, switch_info: dict) -> None:
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
