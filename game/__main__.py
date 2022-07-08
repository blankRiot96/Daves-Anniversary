"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import asyncio
import logging

import pygame

from game.common import HEIGHT, WIDTH
from game.states.enums import States
from game.states.levels import Level
from game.states.main_menu import MainMenu
from game.states.intro import Dialogue

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
        self.state: States = States.DIALOGUE

        # Dictionary to initialize respective game state
        self.perspective_states = {States.LEVEL: Level, States.MAIN_MENU: MainMenu, States.DIALOGUE: Dialogue}
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
            self.state = self.game_state.next_state
            # Creating a new game state from the new state, and passing in
            # the respective switch info for the next game state
            # to access
            self.game_state = self.perspective_states[self.state](
                self.game_state.switch_info
            )

    async def _run(self):
        """
        Async method for WASM compatibility
        """
        while self.alive:
            event_info = self._grab_events()
            for event in event_info["events"]:
                if event.type == pygame.QUIT:
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
