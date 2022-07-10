"""
This file is a part of the 'Unnamed' source code.
The source code is distributed under the MIT license.
"""

import math

import pygame
from game.common import TILE_WIDTH

from game.utils import load_font, pixel_to_tile, get_neighboring_tiles
from library.particles import TextParticle


class Grapple:
    GRAPPLE_RANGE = 12
    GRAPPLE_SPEED = 12

    def __init__(self, player, camera, particle_manager, settings):
        self.GRAPPLE_RANGE = settings["grapple_range"]
        self.GRAPPLE_SPEED = settings["grapple_speed"]
        self.player = player
        self.camera = camera
        self.particle_manager = particle_manager
        self.screen = None  # GOOFINESS ALERT

        self.angle = 0
        self.time_started_hold = 0
        self.clicked = False

        self.dist = 0
        self.on_grapple = False
        self.grappling = False

        self.grapple_startpoint = self.player.vec.copy()
        self.grapple_endpoint = self.player.vec.copy()
        self.grapple_time = 0
        self.grapple_start_player_vec = pygame.Vector2(0, 0)

        self.font = load_font(8)
    
    @staticmethod
    def sigmoid(x):
        return 1 / (1 + math.e ** (-3 * (x - 1)))
    
    def create_text_particle(self, txt):
        self.particle_manager.add(
            TextParticle(
                screen=self.screen,
                image=self.font.render(
                    txt, True, (255, 0, 0)
                ),
                pos=self.player.vec,
                vel=(0, -1.5),
                alpha_speed=3,
                lifespan=80
            )
        )
    
    def _grapple_extend(self, enemies):
        for enemy in enemies:
            if enemy.rect.collidepoint(self.grapple_endpoint):
                return False
        else:
            if self.grapple_startpoint.distance_to(self.grapple_endpoint) <= self.GRAPPLE_RANGE * TILE_WIDTH:
                self.grapple_endpoint.x += math.cos(self.angle) * self.GRAPPLE_SPEED
                self.grapple_endpoint.y += math.sin(self.angle) * self.GRAPPLE_SPEED
        
        return True
    
    def _grapple_pull(self, event_info):
        distance_travelled = self.sigmoid((pygame.time.get_ticks() - self.grapple_time) / 400) * (self.dist - 20)

        new_vec = pygame.Vector2(
            self.grapple_start_player_vec.x + math.cos(self.angle) * distance_travelled,
            self.grapple_start_player_vec.y + math.sin(self.angle) * distance_travelled
        )
        new_vel = pygame.Vector2(
            (new_vec.x - self.player.vec.x) * event_info["dt"],
            (new_vec.y - self.player.vec.y) * event_info["dt"]
        )

        self.player.vel.y = 0
        self.player.vel.x, self.player.vel.y = new_vel.x / 7, new_vel.y / 7

        self.grapple_startpoint = self.player.vec.copy()
    
    def _grapple(self, neighboring_tiles, event_info, enemies):
        for neighboring_tile in neighboring_tiles:
            if neighboring_tile.rect.collidepoint(self.grapple_endpoint):
                if self.dist == 0:
                    self.dist = self.grapple_startpoint.distance_to(self.grapple_endpoint)
                    self.grapple_time = pygame.time.get_ticks()
                    self.grapple_start_player_vec = self.player.vec.copy()
                
                if self.grapple_startpoint.distance_to(self.grapple_endpoint) > 20:
                    self._grapple_pull(event_info)
                else:
                    self.player.vel.x, self.player.vel.y = 0, 0
                break
        else:
            if not self._grapple_extend(enemies):
                self.create_text_particle("Cannot grapple onto enemies")

                self.grapple_endpoint = self.grapple_startpoint
                self.time_started_hold = 0
                self.clicked = False
                self.on_grapple = False
                self.dist = 0

    def update(self, event_info, tilemap, enemies):
        self.grapple_startpoint = self.player.vec.copy()
        self.grappling = False

        for event in event_info["events"]:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.time_started_hold = pygame.time.get_ticks()
                self.clicked = True

            elif event.type == pygame.MOUSEBUTTONUP:
                self.time_started_hold = 0
                self.clicked = False
                self.on_grapple = False
                self.dist = 0
        
        if self.clicked and pygame.time.get_ticks() - self.time_started_hold < 100:
            pass
        elif self.time_started_hold != 0 and pygame.time.get_ticks() - self.time_started_hold > 100:
            if not self.on_grapple:
                self.grapple_endpoint = self.player.vec.copy()
                mouse_pos = pygame.mouse.get_pos()
                adj_grapple_startpoint = self.camera.apply(self.grapple_startpoint)

                self.angle = (math.atan2(
                    mouse_pos[1] - adj_grapple_startpoint.y,
                    mouse_pos[0] - adj_grapple_startpoint.x
                ))

                if not -180 < math.degrees(self.angle) < 0:
                    self.create_text_particle("Cannot grapple downwards")

                self.on_grapple = True

            if -180 < math.degrees(self.angle) < 0:
                self._grapple(get_neighboring_tiles(tilemap, 2, pixel_to_tile(self.grapple_endpoint)), event_info, enemies)
                self.grappling = True
        
        self.clicked = False
    
    def draw(self, screen):
        self.screen = screen  # GOOFINESS ALERT

        if self.grappling:
            e, f = self.camera.apply(self.grapple_startpoint), self.camera.apply(self.grapple_endpoint)
            g, h = pygame.Vector2(e.x, e.y), pygame.Vector2(f.x, f.y)

            pygame.draw.line(screen, (255, 255, 255), g, h, width=2)


class Swing:
    def __init__(self, player, camera):
        self.player = player
        self.camera = camera
        self.angle = 0
        self.angular_vel = 5
        self.time_started_hold = 0
        self.clicked = False

        self.dist = 0
        self.on_grapple = False
        self.grappling = False
        self.extending = False

        self.grapple_startpoint = self.player.vec.copy()
        self.grapple_endpoint = self.player.vec.copy()
        self.grapple_time = 0
        self.grapple_start_player_vec = pygame.Vector2(0, 0)
        self.prev_distance_travelled = 0
        self.previous_player_vec = pygame.Vector2()
        self.exit_velocity = pygame.Vector2()
    
    @staticmethod
    def sigmoid(x):
        return 1 / (1 + math.e ** (-3 * (x - 1)))
    
    def _grapple_extend(self):
        if self.grapple_startpoint.distance_to(self.grapple_endpoint) <= 192:
            self.grapple_endpoint.x += math.cos(self.angle) * 14
            self.grapple_endpoint.y += math.sin(self.angle) * 14
    
    def _grapple(self, neighboring_tiles, event_info, tilemap, enemies):
        for neighboring_tile in neighboring_tiles:
            if neighboring_tile.rect.collidepoint(self.grapple_endpoint):
                if self.dist == 0:
                    self.dist = self.grapple_startpoint.distance_to(self.grapple_endpoint)
                    self.grapple_time = pygame.time.get_ticks()
                    self.grapple_start_player_vec = self.player.vec.copy()
                    self.prev_distance_travelled = 0
                self.player.vel.y = 0
                
                temp_x = math.cos(math.radians(self.angular_vel)) * (self.player.vec.x - self.grapple_endpoint.x) - math.sin(math.radians(self.angular_vel)) * (self.player.vec.y - self.grapple_endpoint.y) + self.grapple_endpoint.x
                temp_y = math.sin(math.radians(self.angular_vel)) * (self.player.vec.x - self.grapple_endpoint.x) + math.cos(math.radians(self.angular_vel)) * (self.player.vec.y - self.grapple_endpoint.y) + self.grapple_endpoint.y

                self.exit_velocity = pygame.Vector2(temp_x - self.player.vec.x, temp_y - self.player.vec.y)

                self.angular_vel += (pygame.Vector2(temp_x - self.grapple_endpoint.x, temp_y - self.grapple_endpoint.y).normalize().x - self.player.vel.x / 12) * 0.18
                self.angular_vel *= 0.995

                for player_neighboring_tile in get_neighboring_tiles(tilemap, 2, self.player.tile_vec):
                    if player_neighboring_tile.rect.colliderect(pygame.Rect(temp_x, temp_y, *self.player.SIZE)):

                        self.angular_vel = 0

                self.player.vec.x = temp_x
                self.player.vec.y = temp_y
                self.player.tile_vec = pixel_to_tile(self.player.vec)
                
                self.player.rect.x = round(self.player.vec.x)
                self.player.rect.y = round(self.player.vec.y)

                self.player.vel.x = 0
                break
        else:
            self._grapple_extend()

    def update(self, event_info, tilemap, enemies):
        self.grapple_startpoint = self.player.vec.copy()
        self.grappling = False

        for event in event_info["events"]:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.time_started_hold = pygame.time.get_ticks()
                self.clicked = True

            elif event.type == pygame.MOUSEBUTTONUP:
                self.time_started_hold = 0
                self.clicked = False
                self.on_grapple = False
                self.dist = 0
                self.player.swing_vel.x = self.exit_velocity.x
                self.player.swing_vel.y = self.exit_velocity.y
                print(self.exit_velocity)

                self.exit_velocity.x, self.exit_velocity.y = 0, 0
        
        if self.clicked and pygame.time.get_ticks() - self.time_started_hold < 100:
            pass
            # print("AIGHT")
            # self._whip()
        elif self.time_started_hold != 0 and pygame.time.get_ticks() - self.time_started_hold > 100:
            if not self.on_grapple:
                self.grapple_endpoint = self.player.vec.copy()
                mouse_pos = pygame.mouse.get_pos()
                adj_grapple_startpoint = self.camera.apply(self.grapple_startpoint)

                self.angle = (math.atan2(
                    mouse_pos[1] - adj_grapple_startpoint.y,
                    mouse_pos[0] - adj_grapple_startpoint.x
                ))

                self.on_grapple = True

            self._grapple(get_neighboring_tiles(tilemap, 2, pixel_to_tile(self.grapple_endpoint)), event_info, tilemap, enemies)
            self.grappling = True
        
        self.clicked = False
    
    def draw(self, screen):
        if self.grappling:
            e, f = self.camera.apply(self.grapple_startpoint), self.camera.apply(self.grapple_endpoint)
            g, h = pygame.Vector2(e.x, e.y), pygame.Vector2(f.x, f.y)

            pygame.draw.line(screen, (0, 0, 0), g, h, width=2)