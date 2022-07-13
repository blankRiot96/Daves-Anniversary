from typing import Optional

import pygame

from game.common import ASSETS_DIR, HEIGHT, WIDTH, EventInfo
from game.states.enums import States
from game.utils import load_font

from library.transition import FadeTransition
from library.ui.buttons import Button
from library.ui.camera import Camera


class InitCreditStage:
    FADE_SPEED = 4
    TITLE_FONT = load_font(32)
    MAIN_FONT = load_font(16)

    def __init__(self, switch_info: dict):
        self.switch_info = switch_info

        self.transition = FadeTransition(True, self.FADE_SPEED, (WIDTH, HEIGHT))
        self.next_state: Optional[States] = None
        self.camera = Camera(WIDTH, HEIGHT)

        self.yscroll = 0

        self.skip_button = Button(
            pos=(WIDTH - 100, HEIGHT - 50),
            size=(100, 50),
            colors={
                "static": (179, 185, 209),
                "hover": (218, 224, 234),
                "text": (20, 16, 19),
            },
            font_name="PixelMillenium",
            text="skip",
            corner_radius=4,
        )

        self.pygame_powered = pygame.transform.scale(pygame.image.load(ASSETS_DIR / "images/credits/pygame_powered.png").convert_alpha(), (270, 105))

class Credits(InitCreditStage):
    def render_center_txt(self, screen, txt, center_pos, font):
        txt_surf = font.render(txt, True, (255, 255, 255))

        e = self.camera.hard_apply(center_pos)
        f = pygame.Vector2(e.x, e.y)

        txt_rect = txt_surf.get_rect(center=f)

        screen.blit(
            txt_surf,
            txt_rect
        )

    def update(self, event_info: EventInfo):
        self.camera.hard_adjust_to(pygame.Vector2(0, self.yscroll))
        self.yscroll += 0.5

        self.transition.update(event_info["dt"])
        self.skip_button.update(event_info["mouse_pos"], event_info["mouse_press"])

        if self.skip_button.clicked or self.yscroll > 600:
            self.transition.fade_in = False

        if self.transition.event:
            self.next_state = States.MAIN_MENU
        # print(self.camera.camera)
    
    def draw(self, screen):

        screen.fill((0, 0, 0))

        self.skip_button.draw(screen)
        
        self.render_center_txt(screen, "Credit to:", (0, 0), self.TITLE_FONT)

        self.render_center_txt(screen, "Developers: Axis#3719, disappointment#8603, SSS_Says_Snek#0194", (0, 150), self.MAIN_FONT)
        self.render_center_txt(screen, "Art mainly done by disappointment, and partly by Axis", (0, 250), self.MAIN_FONT)

        e = self.camera.hard_apply((0, 350))
        f = pygame.Vector2(e.x, e.y)

        screen.blit(
            self.pygame_powered,
            self.pygame_powered.get_rect(center=f)
        )

        self.transition.draw(screen)