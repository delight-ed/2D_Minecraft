import pygame
import random
import math
from src.constants import *

class Mob:
    def __init__(self, mob_type, x, y):
        self.type = mob_type
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.health = 20
        self.max_health = 20
        self.damage = 5
        self.speed = 50
        self.width = 24
        self.height = 32
        self.on_ground = False
        self.ai_timer = 0
        self.target_player = None
        self.attack_cooldown = 0
        self.detection_range = 200
        
        # Set mob-specific properties
        self.setup_mob_properties()
    
    def setup_mob_properties(self):
        if self.type == MOB_ZOMBIE:
            self.health = self.max_health = 30
            self.damage = 8
            self.speed = 40
            self.detection_range = 150
        elif self.type == MOB_SKELETON:
            self.health = self.max_health = 25
            self.damage = 6
            self.speed = 45
            self.detection_range = 200
        elif self.type == MOB_CREEPER:
            self.health = self.max_health = 20
            self.damage = 50  # Explosion damage
            self.speed = 35
            self.detection_range = 100
        elif self.type == MOB_SPIDER:
            self.health = self.max_health = 15
            self.damage = 4
            self.speed = 60
            self.detection_range = 120
        elif self.type == MOB_ENDERMAN:
            self.health = self.max_health = 80
            self.damage = 15
            self.speed = 80
            self.detection_range = 300
            self.height = 48
        elif self.type == MOB_DRAGON:
            self.health = self.max_health = 500
            self.damage = 25
            self.speed = 100
            self.detection_range = 400
            self.width = 64
            self.height = 64
    
    def update(self, dt, world, player):
        # AI behavior
        self.ai_timer += dt
        self.attack_cooldown -= dt
        
        # Check if player is in detection range
        distance_to_player = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
        
        if distance_to_player <= self.detection_range:
            self.target_player = player
        elif distance_to_player > self.detection_range * 1.5:
            self.target_player = None
        
        # AI behavior based on mob type
        if self.target_player:
            self.update_combat_ai(dt, player)
        else:
            self.update_idle_ai(dt)
        
        # Apply gravity
        self.vy -= GRAVITY * dt
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Handle collisions
        self.handle_collisions(world)
        
        # Attack player if close enough
        if self.target_player and distance_to_player < 40 and self.attack_cooldown <= 0:
            self.attack_player(player)
    
    def update_combat_ai(self, dt, player):
        # Move towards player
        dx = player.x - self.x
        dy = player.y - self.y
        
        if abs(dx) > 20:  # Don't move if very close
            if dx > 0:
                self.vx = self.speed
            else:
                self.vx = -self.speed
        else:
            self.vx = 0
        
        # Jump if needed
        if self.on_ground and abs(dy) > 32:
            self.vy = PLAYER_JUMP_SPEED * 0.8
            self.on_ground = False
        
        # Special behavior for creeper (explode when close)
        if self.type == MOB_CREEPER:
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance < 50:
                self.explode(player)
    
    def update_idle_ai(self, dt):
        # Random movement
        if self.ai_timer > 2:
            self.ai_timer = 0
            if random.random() < 0.3:
                self.vx = random.choice([-self.speed * 0.5, 0, self.speed * 0.5])
            
            if self.on_ground and random.random() < 0.1:
                self.vy = PLAYER_JUMP_SPEED * 0.6
                self.on_ground = False
    
    def attack_player(self, player):
        if self.type == MOB_CREEPER:
            return  # Creeper explodes instead
        
        player.take_damage(self.damage)
        self.attack_cooldown = 1.0  # 1 second cooldown
    
    def explode(self, player):
        # Creeper explosion
        distance = math.sqrt((player.x - self.x) ** 2 + (player.y - self.y) ** 2)
        if distance < 100:
            damage = max(10, self.damage - distance // 10)
            player.take_damage(damage)
        
        # Remove creeper (it exploded)
        self.health = 0
    
    def handle_collisions(self, world):
        # Similar to player collision detection
        left = int((self.x - self.width // 2) // BLOCK_SIZE)
        right = int((self.x + self.width // 2) // BLOCK_SIZE)
        bottom = int((self.y - self.height) // BLOCK_SIZE)
        top = int(self.y // BLOCK_SIZE)
        
        # Vertical collision
        self.on_ground = False
        for x in range(left, right + 1):
            if self.vy <= 0:
                block = world.get_block(x, bottom)
                if block.type != BLOCK_AIR and block.type != BLOCK_WATER:
                    self.y = (bottom + 1) * BLOCK_SIZE + self.height
                    self.vy = 0
                    self.on_ground = True
            
            if self.vy > 0:
                block = world.get_block(x, top)
                if block.type != BLOCK_AIR and block.type != BLOCK_WATER:
                    self.y = top * BLOCK_SIZE
                    self.vy = 0
        
        # Horizontal collision
        for y in range(bottom, top + 1):
            if self.vx < 0:
                block = world.get_block(left, y)
                if block.type != BLOCK_AIR and block.type != BLOCK_WATER:
                    self.x = (left + 1) * BLOCK_SIZE + self.width // 2
                    self.vx = 0
            
            if self.vx > 0:
                block = world.get_block(right, y)
                if block.type != BLOCK_AIR and block.type != BLOCK_WATER:
                    self.x = right * BLOCK_SIZE - self.width // 2
                    self.vx = 0
        
        # World boundaries
        self.x = max(self.width // 2, min(self.x, WORLD_WIDTH * BLOCK_SIZE - self.width // 2))
        self.y = max(self.height, self.y)
    
    def take_damage(self, damage):
        self.health -= damage
        self.health = max(0, self.health)
    
    def is_dead(self):
        return self.health <= 0
    
    def render(self, screen, camera):
        screen_x = self.x - camera.x - self.width // 2
        screen_y = SCREEN_HEIGHT - (self.y + camera.y)
        
        color = self.get_mob_color()
        pygame.draw.rect(screen, color, (screen_x, screen_y - self.height, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (screen_x, screen_y - self.height, self.width, self.height), 2)
        
        # Draw health bar
        if self.health < self.max_health:
            bar_width = self.width
            bar_height = 4
            health_ratio = self.health / self.max_health
            
            pygame.draw.rect(screen, RED, (screen_x, screen_y - self.height - 8, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, (screen_x, screen_y - self.height - 8, bar_width * health_ratio, bar_height))
    
    def get_mob_color(self):
        colors = {
            MOB_ZOMBIE: (0, 100, 0),
            MOB_SKELETON: (200, 200, 200),
            MOB_CREEPER: (0, 150, 0),
            MOB_SPIDER: (50, 50, 50),
            MOB_ENDERMAN: (20, 20, 20),
            MOB_DRAGON: (100, 0, 100)
        }
        return colors.get(self.type, GRAY)