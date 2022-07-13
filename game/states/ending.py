import pygame
from game.states.enums import States, Dimensions
from library.tilemap import TileLayerMap
from game.common import MAP_DIR
from game.player import Player
from game.common import WIDTH, HEIGHT, SAVE_DATA
from library.ui.camera import Camera
from library.sfx import SFXManager
from library.sprite.load import load_assets
from library.transition import FadeTransition
from typing import Optional



class InitEndingStage:
    def __init__(self, switch_info) -> None:
        self.switch_info = switch_info

        self.current_dimension = Dimensions(
            SAVE_DATA["latest_dimension"]
        )  # First parallel dimension
        self.latest_checkpoint = SAVE_DATA["latest_checkpoint"]

        self.camera = Camera(WIDTH, HEIGHT)
        self.sfx_manager = SFXManager("level")
        self.assets = load_assets("level")
        self.event_info = {"dt": 0}

        self.tilemap = TileLayerMap(MAP_DIR / "ending.tmx")


        self.transition = FadeTransition(True, self.FADE_SPEED, (WIDTH, HEIGHT))
        self.next_state: Optional[States] = None

        self.settings = {
            enm.value: load_settings(SETTINGS_DIR / f"{enm.value}.json")
            for enm in Dimensions
        }


        self.player = Player(
            self.settings[self.current_dimension.value],
            self.latest_checkpoint,
            self.assets["dave_walk"],
            self.camera,
            self.particle_manager,
        )
    
    def update(*args, **kwargs):
        pass 

    def draw(*args, **kwargs):
        pass

class TransitionStage(InitEndingStage):
    """
    Handles game state transitions
    """

    FADE_SPEED = 4

    def __init__(self, switch_info: dict) -> None:
        super().__init__(switch_info)

        # Store any information needed to be passed
        # on to the next state
        self.switch_info = {}

    def update(self, event_info):
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

class Ending(TransitionStage):
    pass 



