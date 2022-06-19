"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import asyncio

import pygame

from game.states.enums import States
from game.states.levels import Level


class Game:
    """
    Handles game
    """
    SCREEN_SIZE = (420, 200)
    FPS_CAP = 120

    def __init__(self):
        """
        Initialize Game class
        """
        self.alive = True
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE, pygame.SCALED)
        self.state: States = States.LEVEL

        # Dictionary to initialize respective game state
        self.perspective_states = {
            States.LEVEL: Level,
        }
        self.game_state = self.perspective_states[self.state]()
        self.clock = pygame.time.Clock()

    def _grab_events(self):
        """
        Return window events 
        """
        raw_dt = self.clock.get_time() / 1000
        dt = raw_dt * 100
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
            "key_press": key_press
        }

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

            self.screen.fill("lightblue")
            self.game_state.draw(self.screen)
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
