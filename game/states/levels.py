"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import abc
import logging
from typing import Optional

import pygame

from game.common import HEIGHT, MAP_DIR, SETTINGS_DIR, WIDTH, EventInfo
from game.enemy import MovingWall
from game.player import Player
from game.portal import Portal
from game.sound_icon import SoundIcon
from game.states.enums import Dimensions, States
from game.utils import load_font, load_settings
from library.effects import ExplosionManager
from library.particles import ParticleManager, TextParticle
from library.sfx import SFXManager
from library.sprite.load import load_assets
from library.tilemap import TileLayerMap
from library.transition import FadeTransition
from library.ui.buttons import Button
from library.ui.camera import Camera
from game.background import BackGroundEffect

logger = logging.getLogger()


class InitLevelStage(abc.ABC):
    def __init__(self, switch_info: dict) -> None:
        self.switch_info = switch_info
        self.current_dimension = Dimensions.PARALLEL_DIMENSION
        """
        Initialize some attributes
        """
        self.camera = Camera(WIDTH, HEIGHT)
        self.sfx_manager = SFXManager("level")
        self.assets = load_assets("level")
        self.event_info = {
            "dt": 0
        }

        self.transition = FadeTransition(True, self.FADE_SPEED, (WIDTH, HEIGHT))
        self.next_state: Optional[States] = None

        self.settings = {
            "parallel_dimension": load_settings(
                SETTINGS_DIR / f"{Dimensions.PARALLEL_DIMENSION.value}.json"
            ),
            "alien_dimension": load_settings(
                SETTINGS_DIR / f"{Dimensions.ALIEN_DIMENSION.value}.json"
            ),
            "volcanic_dimension": load_settings(
                SETTINGS_DIR / f"{Dimensions.VOLCANIC_DIMENSION.value}.json"
            ),
            # "water_dimension": load_settings(
            #     SETTINGS_DIR / f"{Dimensions.WATER_DIMENSION.value}.json"
            # ),
            # "moon_dimension": load_settings(
            #     SETTINGS_DIR / f"{Dimensions.MOON_DIMENSION.value}.json"
            # ),
            # "homeland_dimension": load_settings(
            #     SETTINGS_DIR / f"{Dimensions.HOMELAND_DIMENSION.value}.json"
            # ),
        }
        self.dimensions_traveled = {self.current_dimension}
        self.enemies = set()
        self.portals = set()
        self.particle_manager = ParticleManager(self.camera)


class RenderBackgroundStage(InitLevelStage):
    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)
        self.background_manager = BackGroundEffect(self.assets)
    
    def update(self):
        self.background_manager.update(self.event_info)
    
    def draw(self, screen):
        self.background_manager.draw(screen, self.camera)


class TileStage(RenderBackgroundStage):
    """
    Handles tilemap rendering
    """

    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)
        # self.tilemap = TileLayerMap(MAP_DIR / f"{self.current_dimension.value}.tmx")
        self.tilemap = TileLayerMap(MAP_DIR / "dimension_one.tmx")

        self.map_surf = self.tilemap.make_map()

        for enemy_obj in self.tilemap.tilemap.get_layer_by_name("enemies"):
            if enemy_obj.name == "moving_wall":
                self.enemies.add(
                    MovingWall(self.settings[self.current_dimension.value], enemy_obj)
                )

        self.tilesets = {enm: self.assets[enm.value] for enm in Dimensions}

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        screen.blit(self.map_surf, self.camera.apply((0, 0)))


class PlayerStage(TileStage):
    """
    Handle player related actions
    """

    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)

        self.player = Player(
            self.settings[self.current_dimension.value], self.assets["dave_walk"]
        )

    def update(self, event_info: EventInfo):
        super().update()
        self.player.update(event_info, self.tilemap, self.enemies)
        self.event_info = event_info

        # Temporary checking here
        if self.player.y > 2000:
            self.player.alive = False

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        self.player.draw(self.event_info["dt"], screen, self.camera)


class SpecialTileStage(PlayerStage):
    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)

    def update(self, event_info: EventInfo):
        super().update(event_info)

        for special_tiles in self.tilemap.special_tiles.values():
            special_tiles.update(self.player)


class EnemyStage(SpecialTileStage):
    def update(self, event_info: EventInfo):
        super().update(event_info)

        for enemy in self.enemies:
            enemy.update(event_info, self.tilemap, self.player)

    def draw(self, screen: pygame.Surface):
        for enemy in self.enemies:
            enemy.draw(self.event_info["dt"], screen, self.camera)

        super().draw(screen)


class PortalStage(EnemyStage):
    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)

        for portal_obj in self.tilemap.tilemap.get_layer_by_name("portals"):
            if portal_obj.name == "portal":
                self.portals.add(
                    Portal(portal_obj, [enm for enm in Dimensions], self.assets)
                )

    def update(self, event_info: EventInfo):
        super().update(event_info)

        for portal in self.portals:
            # if we aren't changing the dimension,
            # we have to reset portal's dimension to the current one
            if not portal.dimension_change:
                portal.current_dimension = self.current_dimension
            # otherwise (if we're switching dimension)
            else:
                print(f"Changed dimension to: {portal.current_dimension}")

                self.current_dimension = portal.current_dimension
                self.map_surf = self.tilemap.make_map(
                    self.tilesets[self.current_dimension]
                )

                # change player's settings
                self.player.change_settings(self.settings[self.current_dimension.value])
                # change enemy settings
                for enemy in self.enemies:
                    enemy.change_settings(self.settings[self.current_dimension.value])

            portal.update(self.player, event_info)

    def draw(self, screen: pygame.Surface):
        for portal in self.portals:
            if portal.dimension_change:
                font = load_font(8)
                formatted_txt = portal.current_dimension.value.replace("_", " ").title()

                text_particle = TextParticle(
                    screen=screen,
                    image=font.render(
                        f"Switched to: {formatted_txt}", True, (255, 255, 255)
                    ),
                    pos=self.player.vec,
                    vel=(0, -1.5),
                    alpha_speed=3,
                    lifespan=80,
                )

                if portal.current_dimension not in self.dimensions_traveled:
                    self.dimensions_traveled.add(portal.current_dimension)

                    self.transition.fade_out_in(
                        on_finish=lambda: self.particle_manager.add(text_particle)
                    )
                else:
                    self.particle_manager.add(text_particle)

            portal.draw(screen, self.camera)

        super().draw(screen)


class CameraStage(PortalStage):
    def update(self, event_info: EventInfo):
        super().update(event_info)

        self.camera.adjust_to(event_info["dt"], self.player.rect)


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
        self.particle_manager.update(event_info)

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
        self.particle_manager.draw()


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
