"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import abc
from asyncio import events
import logging
from typing import Optional

import pygame

from game.background import BackGroundEffect
from game.common import (ASSETS_DIR, HEIGHT, MAP_DIR, SAVE_DATA, SETTINGS_DIR, WIDTH,
                         EventInfo)
from game.enemy import MovingPlatform, MovingWall, Ungrappleable
from game.interactables.checkpoint import Checkpoint
from game.interactables.notes import Note
from game.interactables.portal import Portal
from game.interactables.ring import Ring
from game.interactables.sound_icon import SoundIcon
from game.player import Player
from game.shooter import Shooter
from game.states.enums import Dimensions, States
from game.utils import load_font, load_settings
from library.effects import ExplosionManager
from library.particles import ParticleManager, TextParticle
from library.sfx import SFXManager
from library.sprite.load import load_assets
from library.tilemap import TileLayerMap
from library.tiles import SpikeTile
from library.transition import FadeTransition
from library.ui.buttons import Button
from library.ui.camera import Camera
from library.ui.healthbar import PlayerHealthBar

logger = logging.getLogger()


class InitLevelStage(abc.ABC):
    def __init__(self, switch_info: dict) -> None:
        """
        Initialize some attributes
        """

        self.switch_info = switch_info
        self.current_dimension = Dimensions(
            SAVE_DATA["latest_dimension"]
        )  # First parallel dimension
        self.latest_checkpoint = SAVE_DATA["latest_checkpoint"]

        self.camera = Camera(WIDTH, HEIGHT)
        self.sfx_manager = SFXManager("level")
        self.assets = load_assets("level")
        self.event_info = {"dt": 0}

        self.tilemap = TileLayerMap(MAP_DIR / "dimension_one.tmx")

        self.transition = FadeTransition(True, self.FADE_SPEED, (WIDTH, HEIGHT))
        self.next_state: Optional[States] = None

        self.settings = {
            enm.value: load_settings(SETTINGS_DIR / f"{enm.value}.json")
            for enm in Dimensions
        }

        self.unlocked_dimensions = [
            Dimensions.PARALLEL_DIMENSION,
            Dimensions.VOLCANIC_DIMENSION,
        ]

        self.dimensions_traveled = {self.current_dimension}
        self.enemies = set()
        self.portals = set()
        self.notes = set()
        self.spikes = set()
        self.particle_manager = ParticleManager(self.camera)

        self.latest_checkpoint_id = SAVE_DATA["latest_checkpoint_id"]

        self.checkpoints = {
            Checkpoint(
                pygame.Rect(obj.x, obj.y, obj.width, obj.height), self.particle_manager, obj.unlock_dimension, obj.c_id
            )
            for obj in self.tilemap.tilemap.get_layer_by_name("checkpoints")
        }

        self.ring = [Ring(pygame.image.load(ASSETS_DIR / "images/ring.png"), (obj.x, obj.y), self.particle_manager) for obj in self.tilemap.tilemap.get_layer_by_name("ring")][0]
        self.ring.on_ground = not SAVE_DATA["has_ring"]

        self.num_extra_dims_unlocked = SAVE_DATA["num_extra_dims_unlocked"]

        for portal_obj in self.tilemap.tilemap.get_layer_by_name("portals"):
            if portal_obj.name == "portal":
                self.portals.add(
                    Portal(portal_obj, self.unlocked_dimensions, self.assets["portal"])
                )

        len_unlocked_dims = len(self.unlocked_dimensions)
        for dimension in list(Dimensions)[len_unlocked_dims:len_unlocked_dims + self.num_extra_dims_unlocked]:
            self.unlocked_dimensions.append(dimension)

        self.player = Player(
            self.settings[self.current_dimension.value],
            self.latest_checkpoint,
            self.assets["dave_walk"],
            self.camera,
            self.particle_manager,
            SAVE_DATA["has_ring"]
        )
        self.player.ring_img = self.ring.non_interacting_img

        self.explosion_manager = ExplosionManager("fire")
        self.turret_explosioner = ExplosionManager("turret")

        self.paused = False

    def update(*args, **kwargs):
        pass

    def draw(*args, **kwargs):
        pass


class RenderBackgroundStage(InitLevelStage):
    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)
        self.background_manager = BackGroundEffect(self.assets)

    def update(self):
        self.background_manager.update(self.event_info)

    def draw(self, screen):
        self.background_manager.draw(screen, self.camera, self.current_dimension)


class RenderCheckpointStage(RenderBackgroundStage):
    def draw(self, screen: pygame.Surface):
        super().draw(screen)

        for checkpoint in self.checkpoints:
            checkpoint.draw(screen)


class RenderPortalStage(RenderCheckpointStage):
    def draw(self, screen: pygame.Surface):
        super().draw(screen)

        for portal in self.portals:
            if portal.dimension_change:
                font = load_font(8)
                formatted_txt = portal.current_dimension.value.replace("_", " ").title()

                text_particle = TextParticle(
                    screen=screen,
                    image=font.render(
                        f"Switched to: {formatted_txt}", True, (218, 224, 234)
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


class RenderNoteStage(RenderPortalStage):
    def draw(self, screen):
        super().draw(screen)
        for note in self.notes:
            note.draw(screen, self.camera)


class RenderEnemyStage(RenderNoteStage):
    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        for enemy in self.enemies:
            if enemy.name == "ungrappleable":
                continue

            enemy.draw(self.event_info["dt"], screen, self.camera)


class ShooterStage(RenderEnemyStage):
    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)
        self.shooters = {
            Shooter(self.assets["shooter"], obj)
            for obj in self.tilemap.tilemap.get_layer_by_name("shooters")
        }

    def update(self) -> None:
        super().update()

        for shooter in set(self.shooters):
            dm, vec, pos = shooter.update(self.player, self.event_info["dt"])
            if vec:
                self.explosion_manager.create_explosion(self.camera.apply(vec).topleft)
            
            if dm:
                self.player.hp -= dm

            if pos:
                self.turret_explosioner.create_explosion(self.camera.apply(pos).topleft)

            if not shooter.alive:
                self.shooters.remove(shooter)

    def draw(self, screen: pygame.Surface) -> None:
        super().draw(screen)

        for shooter in self.shooters:
            shooter.draw(screen, self.camera)


class TileStage(ShooterStage):
    """
    Handles tilemap rendering
    """

    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)
        # self.tilemap = TileLayerMap(MAP_DIR / f"{self.current_dimension.value}.tmx"

        self.tilesets = {enm: self.assets[enm.value] for enm in Dimensions}

        self.map_surf = self.tilemap.make_map(self.tilesets[self.current_dimension])

        for enemy_obj in self.tilemap.tilemap.get_layer_by_name("enemies"):
            if enemy_obj.name == "moving_wall":
                self.enemies.add(
                    MovingWall(
                        self.settings[self.current_dimension.value],
                        enemy_obj,
                        self.assets,
                    )
                )
            elif enemy_obj.name == "moving_platform":
                self.enemies.add(
                    MovingPlatform(
                        self.settings[self.current_dimension.value],
                        enemy_obj,
                        self.tilesets[self.current_dimension],
                    )
                )
            elif enemy_obj.name == "ungrappleable":
                self.enemies.add(
                    Ungrappleable(
                        enemy_obj
                    )
                )

        for spike_obj in self.tilemap.tilemap.get_layer_by_name("spikes"):
            if spike_obj.name == "spike":
                self.spikes.add(SpikeTile(self.assets["spike"], spike_obj))

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        screen.blit(self.map_surf, self.camera.apply((0, 0)))


class PlayerStage(TileStage):
    """
    Handle player related actions
    """

    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)

        # self.player = Player(
        #     self.settings[self.current_dimension.value], self.assets["dave_walk"]
        # )

    def update(self, event_info: EventInfo):
        super().update()

        self.ring.update(self.player.rect, self.player)

        self.player.update(event_info, self.tilemap, self.enemies, self.ring)
        self.event_info = event_info

        # Temporary checking here
        if self.player.y > 2500:
            self.player.alive = False

    def draw(self, screen: pygame.Surface):
        super().draw(screen)

        self.ring.draw(screen, self.camera)

        self.player.draw(screen, self.camera)


class ItemStage(PlayerStage):
    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)

    def draw(self, screen):
        super().draw(screen)
        # self.grapple.draw(screen)

    def update(self, event_info: EventInfo):
        super().update(event_info)
        # self.grapple.update(event_info, self.tilemap, self.enemies)


class SpecialTileStage(ItemStage):
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
            if enemy.name == "ungrappleable":
                continue
            
            if enemy.name == "moving_platform":
                enemy.update(event_info, self.tilemap, self.player, self.shooters)
            else:
                enemy.update(event_info, self.tilemap, self.player)


class SpikeStage(EnemyStage):
    def update(self, event_info: EventInfo):
        super().update(event_info)

        for spike in self.spikes:
            spike.update(self.player)

    def draw(self, screen: pygame.Surface):
        super().draw(screen)

        for spike in self.spikes:
            spike.draw(screen, self.camera)


class CheckpointStage(SpikeStage):
    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)

    def update(self, event_info: EventInfo):
        super().update(event_info)

        latest_checkpoint_id_cp = self.latest_checkpoint_id

        for checkpoint in self.checkpoints:

            if not checkpoint.text_spawned and checkpoint.rect.colliderect(
                self.player.rect
            ) and (checkpoint.id > self.latest_checkpoint_id or checkpoint.id == 0):
                self.latest_checkpoint = checkpoint.rect.midbottom
                SAVE_DATA["latest_checkpoint"] = self.latest_checkpoint

                self.latest_checkpoint_id = checkpoint.id
                SAVE_DATA["latest_checkpoint_id"] = self.latest_checkpoint_id

                if checkpoint.unlock_dimension:
                    
                    try:
                        self.unlocked_dimensions.append(
                            list(Dimensions)[len(self.unlocked_dimensions)]
                        )
                    except IndexError:
                        continue

                    SAVE_DATA["num_extra_dims_unlocked"] += 1

                    for portal in self.portals:
                        portal.unlock_dimension(self.unlocked_dimensions)

                self.player.hp = 100

            checkpoint.update(self.player.rect, latest_checkpoint_id_cp)


class NoteStage(CheckpointStage):
    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)
        self.notes = {
            Note(self.assets["note"], (obj.x, obj.y), obj.properties["text"])
            for obj in self.tilemap.tilemap.get_layer_by_name("notes")
        }

    def update(self, event_info: EventInfo):
        super().update(event_info)
        for note in self.notes:
            note.update(event_info, self.player.rect)


class PortalStage(NoteStage):
    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)

        """for portal_obj in self.tilemap.tilemap.get_layer_by_name("portals"):
            if portal_obj.name == "portal":
                self.portals.add(
                    Portal(portal_obj, self.unlocked_dimensions, self.assets["portal"])
                )"""

    def update(self, event_info: EventInfo):
        super().update(event_info)

        for portal in self.portals:
            # if we aren't changing the dimension,
            # we have to reset portal's dimension to the current one
            if not portal.dimension_change:
                portal.current_dimension = self.current_dimension
                SAVE_DATA["latest_dimension"] = self.current_dimension.value
            # otherwise (if we're switching dimension)
            else:
                logger.info(f"Changed dimension to: {portal.current_dimension}")

                self.current_dimension = portal.current_dimension
                self.map_surf = self.tilemap.make_map(
                    self.tilesets[self.current_dimension]
                )

                # change player's settings
                self.player.change_settings(self.settings[self.current_dimension.value])
                # change enemy settings
                for enemy in self.enemies:
                    if enemy.name == "ungrappleable":
                        continue

                    enemy.change_settings(self.settings[self.current_dimension.value])

                    if enemy.name == "moving_platform":
                        enemy.surf = enemy.assemble_img(
                            self.tilesets[self.current_dimension]
                        )

            portal.update(self.player, event_info)

        # Unlocking dimensions
        for event in event_info["events"]:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_5:
                for dimension in Dimensions:
                    if dimension not in self.unlocked_dimensions:
                        self.unlocked_dimensions.append(dimension)
                        break

                for portal in self.portals:
                    portal.unlock_dimension(self.unlocked_dimensions)


class CameraStage(PortalStage):
    def update(self, event_info: EventInfo):
        super().update(event_info)

        self.camera.adjust_to(event_info["dt"], self.player.rect)


class UIStage(CameraStage):
    """
    Handles buttons
    """

    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)
        self.buttons = ()
        self.healthbar = PlayerHealthBar(self.player, self.particle_manager, (10, 10), 180, 15)

    def update(self, event_info: EventInfo):
        """
        Update the Button state

        Parameters:
            event_info: Information on the window events
        """
        super().update(event_info)
        for button in self.buttons:
            button.update(event_info["mouse_pos"], event_info["mouse_press"])

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

        self.healthbar.draw(screen)
        self.particle_manager.draw()


class SFXStage(UIStage):
    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)
        stub_rect = pygame.Rect(0, 0, 16, 16)
        stub_rect.topright = pygame.Surface((WIDTH, HEIGHT)).get_rect().topright
        stub_rect.topright = (stub_rect.topright[0] - 32, stub_rect.topright[1] + 16)
        self.sound_icon = SoundIcon(
            self.sfx_manager, self.assets, center_pos=stub_rect.center
        )

        self.sfx_manager.set_volume(SAVE_DATA["last_volume"] * 100)
        self.sound_icon.slider.value = (
            SAVE_DATA["last_volume"] * self.sound_icon.slider.max_value
        )

    def update(self, event_info: EventInfo):
        super().update(event_info)
        self.sound_icon.update(event_info)

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        self.sound_icon.draw(screen)


class ExplosionStage(SFXStage):

    def update(self, event_info: EventInfo) -> None:
        super().update(event_info)
        self.explosion_manager.update(event_info["dt"])
        self.turret_explosioner.update(event_info["dt"])

        # for event in event_info["events"]:
        #     if event.type == pygame.MOUSEBUTTONDOWN:

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        self.explosion_manager.draw(screen)
        self.turret_explosioner.draw(screen)


class PauseStage(ExplosionStage):
    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)

        self.bg_darkener = pygame.Surface((WIDTH, HEIGHT))
        self.bg_darkener.set_alpha(150)

        button_texts = ("main menu", "continue")
        button_pad_y = 20
        self.pause_buttons = [
            Button(
                pos=(WIDTH - 140, HEIGHT - (((30 + button_pad_y) * index) + 50)),
                size=(120, 30),
                colors={
                    "static": (51, 57, 65),
                    "hover": (74, 84, 98),
                    "text": (179, 185, 209),
                },
                font_name=None,
                text=text,
                corner_radius=3,
            )
            for index, text in enumerate(button_texts)
        ]

    def update(self, event_info: EventInfo):
        for event in event_info["events"]:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused

        if not self.paused:
            super().update(event_info)
            return

        for button in self.pause_buttons:
            button.update(event_info["mouse_pos"], event_info["mouse_press"])

            if button.clicked:
                if button.text == "continue":
                    self.paused = False
                elif button.text == "main menu":
                    self.next_state = States.MAIN_MENU

    def draw(self, screen: pygame.Surface):
        super().draw(screen)

        if not self.paused:
            return

        for button in self.pause_buttons:
            button.draw(screen)

        screen.blit(self.bg_darkener, (0, 0))


class TransitionStage(PauseStage):
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
                self.next_state = States.LEVEL

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
