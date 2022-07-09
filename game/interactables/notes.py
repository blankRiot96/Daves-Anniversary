import pygame
from game.common import EventInfo, FONT_DIR
from library.common import Pos
from library.ui.camera import Camera
from library.utils.classes import Expansion
from game.interactables.abc import Interactable


class Note(Interactable):
    """
    A note is a critical component of the game 
    to guide the users to controls without a lengthy
    paragraph about it. This allows users to
    learn the game as they play it, and jump right into
    it.  
    """
    FONT = pygame.font.Font(FONT_DIR / "PixelMillenium.ttf", 8)

    def __init__(self, imgs, pos: Pos, text: str) -> None:
        super().__init__(imgs[0], imgs[1], pos) 
        self.alpha_expansion = Expansion(
            0,
            0,
            255,
            speed=3.3
        )
        self.text = text
        self.text_surf = self.FONT.render(self.text, True, (100, 100, 100))
        self.text_rect = self.text_surf.get_rect(midbottom=(
            pos[0],
            pos[1] - 20
        ))

    
    def update(self, event_info: EventInfo, player_rect: pygame.Rect) -> None:
        super().update(player_rect)
        self.alpha_expansion.update(self.interacting, event_info["dt"])
        self.text_surf.set_alpha(int(self.alpha_expansion.number))
        

    def draw(self, screen: pygame.Surface, camera: Camera) -> None:
        super().draw(screen, camera)
        screen.blit(self.text_surf, camera.apply(self.text_rect))

