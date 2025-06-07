import pygame
import random
import math
from src.world import World
from src.player import Player
from src.camera import Camera
from src.ui import UI
from src.mob_manager import MobManager
from src.item_manager import ItemManager
from src.constants import *

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.world = World()
        self.player = Player(WORLD_WIDTH * BLOCK_SIZE // 2, 100)
        self.camera = Camera()
        self.ui = UI()
        self.mob_manager = MobManager()
        self.item_manager = ItemManager()
        self.state = STATE_PLAYING
        self.day_night_cycle = 0
        self.is_day = True
        
        # Generate initial world
        self.world.generate_world()
        
        # Spawn initial mobs
        self.spawn_initial_mobs()
    
    def spawn_initial_mobs(self):
        for _ in range(10):  # Reduced from 20 to 10
            x = random.randint(100, WORLD_WIDTH * BLOCK_SIZE - 100)
            y = self.world.get_surface_height(x // BLOCK_SIZE) * BLOCK_SIZE - 50
            mob_type = random.choice([MOB_ZOMBIE, MOB_SKELETON, MOB_SPIDER])
            self.mob_manager.spawn_mob(mob_type, x, y)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self.state = STATE_INVENTORY if self.state == STATE_PLAYING else STATE_PLAYING
            elif event.key == pygame.K_c:
                self.state = STATE_CRAFTING if self.state == STATE_PLAYING else STATE_PLAYING
            elif event.key == pygame.K_ESCAPE:
                if self.state != STATE_PLAYING:
                    self.state = STATE_PLAYING
        
        if self.state == STATE_PLAYING:
            self.player.handle_event(event, self.world)
        
        self.ui.handle_event(event, self.state)
    
    def update(self, dt):
        if self.state == STATE_PLAYING:
            self.player.update(dt, self.world)
            self.mob_manager.update(dt, self.world, self.player)
            self.item_manager.update(dt, self.player)
            
            # Update day/night cycle
            self.day_night_cycle += dt * 0.1
            if self.day_night_cycle >= 2 * math.pi:
                self.day_night_cycle = 0
            self.is_day = self.day_night_cycle < math.pi
            
            # Spawn mobs at night
            if not self.is_day and random.random() < 0.001:
                self.spawn_night_mob()
        
        self.camera.update(self.player)
        self.ui.update(dt, self.player)
    
    def spawn_night_mob(self):
        x = self.player.x + random.randint(-500, 500)
        x = max(100, min(x, WORLD_WIDTH * BLOCK_SIZE - 100))
        y = self.world.get_surface_height(x // BLOCK_SIZE) * BLOCK_SIZE - 50
        mob_type = random.choice([MOB_ZOMBIE, MOB_SKELETON, MOB_CREEPER])
        self.mob_manager.spawn_mob(mob_type, x, y)
    
    def render(self):
        # Apply day/night lighting
        if self.is_day:
            self.screen.fill(LIGHT_BLUE)
        else:
            darkness = int(50 + 50 * abs(math.cos(self.day_night_cycle)))
            self.screen.fill((darkness, darkness, darkness + 20))
        
        # Render world
        self.world.render(self.screen, self.camera)
        
        # Render entities
        self.mob_manager.render(self.screen, self.camera)
        self.item_manager.render(self.screen, self.camera)
        self.player.render(self.screen, self.camera)
        
        # Render UI
        self.ui.render(self.screen, self.player, self.state)