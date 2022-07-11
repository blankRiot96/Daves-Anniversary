"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import asyncio
import json
import logging

import pygame

from game.common import AUDIO_DIR, DATA_DIR, HEIGHT, SAVE_DATA, WIDTH
from game.states.enums import States
from game.states.intro import Dialogue
from game.states.levels import Level
from game.states.main_menu import MainMenu

logger = logging.getLogger()


class Game:
    """
    Handles game
    """

    FPS_CAP = 60

    def __init__(self):
        """
        Initialize Game class
        """
        self.logging_config()

        self.alive = True
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
        if SAVE_DATA["first_time"]:
            self.state: States = States.DIALOGUE
        else:
            self.state = States.MAIN_MENU

        # Dictionary to initialize respective game state
        self.perspective_states = {
            States.LEVEL: Level,
            States.MAIN_MENU: MainMenu,
            States.DIALOGUE: Dialogue,
        }
        self.game_state = self.perspective_states[self.state]({})
        self.clock = pygame.time.Clock()

    def _grab_events(self):
        """
        Return window events
        """
        raw_dt = self.clock.get_time() / 1000
        # capping delta time to avoid bugs when moving the window
        dt = min(raw_dt * 100, 10)
        events = pygame.event.get()
        mouse_press = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        key_press = pygame.key.get_pressed()

        return {
            "raw_dt": raw_dt,
            "dt": dt,
            "events": events,
            "mouse_press": mouse_press,
            "mouse_pos": mouse_pos,
            "key_press": key_press,
        }

    def logging_config(self):
        logging.basicConfig()
        logger.setLevel("INFO")

    def _handle_state_switch(self):
        """
        Handle dynamic switching of game states
        """

        if self.game_state.next_state is not None:
            self._save()
            self.state = self.game_state.next_state
            # Creating a new game state from the new state, and passing in
            # the respective switch info for the next game state
            # to access
            self.game_state = self.perspective_states[self.state](
                self.game_state.switch_info
            )

    def _save(self) -> None:
        """
        Saves all game related config
        for future games.
        """
        SAVE_DATA["first_time"] = False
        if self.state == States.LEVEL:
            SAVE_DATA["last_volume"] = self.game_state.sound_icon.slider.value / 100
            print(SAVE_DATA["last_volume"])

        with open(DATA_DIR / "save.json", "w") as f:
            json.dump(SAVE_DATA, f, indent=2)

    async def _run(self):
        """
        Async method for WASM compatibility
        """
        while self.alive:
            event_info = self._grab_events()
            for event in event_info["events"]:
                if event.type == pygame.QUIT:
                    self._save()
                    self.alive = False

            self.game_state.update(event_info)

            self.screen.fill("grey19")
            self.game_state.draw(self.screen)

            pygame.display.set_caption(
                f"Dave's Anniversary: {self.clock.get_fps():.1f} FPS"
            )

            self._handle_state_switch()
            self.clock.tick(self.FPS_CAP)
            pygame.display.flip()
            await asyncio.sleep(0)

    def run(self):
        """
        Runs the game
        """
        asyncio.run(self._run())


if __name__ == "__main__":
    game = Game()
    game.run()
