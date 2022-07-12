from cgi import test
import re
import pygame
import math
from library.utils.funcs import get_movement, circle_surf
from library.utils.classes import Time 
from library.common import Pos
from library.effects.explosions import ExplosionManager


class _Bullet:
    SIZE = 3
    DAMAGE = 20

    def __init__(self, pos: Pos, angle: float, speed: float, max_dist: int) -> None:
        """
        Parameters:
            angle: angle in radians
        """
        self.img = circle_surf(self.SIZE, (100, 98, 25))
        self.angle = angle 
        self.dx, self.dy = get_movement(angle, speed)
        self.vec = pygame.Vector2(pos)
        self.rect = self.img.get_rect()
        self.distance_covered = 0
        self.alive = True
        self.max_dist = max_dist

    def update(self, dt):
        self.vec.x += self.dx * dt 
        self.vec.y += self.dy * dt 
        self.distance_covered += math.sqrt(((self.dx * dt) ** 2) + ((self.dy * dt) ** 2))
        self.rect.center = self.vec
        
        if self.distance_covered > self.max_dist:
            self.alive = False


    def draw(self, screen, camera):
        screen.blit(self.img, camera.apply(self.vec))


class Shooter:
    BULLET_SPEED = 5.3

    def __init__(self, image: pygame.Surface, obj) -> None:
        self.obj = obj 
        self.angle = obj.properties["angle"]
        self.image = pygame.transform.rotate(image,
        obj.properties["angle"])
        self.pos = (obj.x, obj.y)
        self.rect = self.image.get_bounding_rect()
        self.rect.topleft = self.pos
        self.bullets = set()
        self.bullet_gen_time = Time(obj.properties["cooldown"])
        self.alive = True
    
    def update(self, player, dt):
        test_value = [0, 0, 0]
        if self.bullet_gen_time.update():
            self.bullets.add(
                _Bullet(
                    self.rect.center,
                    -math.radians(self.angle),
                    self.BULLET_SPEED,
                    max_dist=self.obj.properties["max_dist"]
                )
            )
        
        if player.rect.colliderect(self.rect) and not player.touched_ground:
            self.alive = False
            test_value[2] = self.pos

        for bullet in set(self.bullets):
            bullet.update(dt)

            if bullet.rect.colliderect(player.rect):
                test_value[0] = bullet.DAMAGE
                bullet.alive = False

            if not bullet.alive:
                test_value[1] = bullet.vec
                self.bullets.remove(bullet)
        
        
        return test_value
            

    def draw(self, screen, camera):
        for bullet in self.bullets:
            bullet.draw(screen, camera)

        screen.blit(self.image, camera.apply(self.rect))


