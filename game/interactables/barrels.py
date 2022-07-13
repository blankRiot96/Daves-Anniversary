import pygame
from library.common import Pos 
from game.interactables.abc import Interactable


class EasterEgg:
    def __init__(self, img, pos) -> None:
        self.img = img 
        self.vec = pygame.Vector2(pos)
        self.max_l = self.vec.y + 7.5, self.vec.y - 7.5
        self.going_up = True
        self.rect = self.img.get_rect(topleft=pos)
        self.picked_up = False
    
    def update(self, player_rect, dt):
        if self.rect.colliderect(player_rect):
            self.picked_up = True
            return 

        if self.going_up:
            if self.vec.y < self.max_l[0]:
                self.vec.y += 0.3 * dt
            else:
                self.going_up = False
        else:
            if self.vec.y > self.max_l[1]:
                self.vec.y -= 0.3 * dt
            else:
                self.going_up = True
        self.rect.topleft = self.vec

    def draw(self, screen, camera):
        screen.blit(self.img, camera.apply(self.rect))


class Barrel(Interactable):
    def __init__(self, imgs, pos: Pos, properties) -> None:
        super().__init__(imgs[0], imgs[1], pos)
        self.alive = True 
        
        ###  EASTER  ###
        self.contains_easter_egg = properties.get("easter", False)
        ###   EGG    ###

    def update(self, events, player_rect):
        super().update(player_rect)
        if not self.interacting:
            return 
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    self.alive = False



