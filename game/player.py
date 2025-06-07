import pygame
from .constants import *

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = BLOCK_SIZE - 4
        self.height = BLOCK_SIZE * 2 - 4
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.jump_power = 15
        self.gravity = 0.8
        self.on_ground = False
        self.inventory = {}
        
        # Add some starting blocks
        self.inventory[BLOCK_DIRT] = 10
        self.inventory[BLOCK_STONE] = 5
    
    def update(self, world):
        """Update player physics and position"""
        # Apply gravity
        self.vel_y += self.gravity
        
        # Limit fall speed
        if self.vel_y > 20:
            self.vel_y = 20
        
        # Move horizontally
        new_x = self.x + self.vel_x
        if not self.check_collision(world, new_x, self.y):
            self.x = new_x
        
        # Move vertically
        new_y = self.y + self.vel_y
        if self.check_collision(world, self.x, new_y):
            if self.vel_y > 0:  # Falling
                self.on_ground = True
            self.vel_y = 0
        else:
            self.y = new_y
            self.on_ground = False
    
    def check_collision(self, world, x, y):
        """Check collision with world blocks"""
        # Check corners of player rectangle
        corners = [
            (x, y),
            (x + self.width, y),
            (x, y + self.height),
            (x + self.width, y + self.height)
        ]
        
        for corner_x, corner_y in corners:
            block_x = int(corner_x // BLOCK_SIZE)
            block_y = int(corner_y // BLOCK_SIZE)
            if world.is_solid(block_x, block_y):
                return True
        return False
    
    def handle_input(self, keys):
        """Handle player input"""
        self.vel_x = 0
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vel_x = -self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vel_x = self.speed
        if (keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vel_y = -self.jump_power
    
    def mine_block(self, world, mouse_x, mouse_y, camera_x, camera_y):
        """Mine block at mouse position"""
        world_x = int((mouse_x + camera_x) // BLOCK_SIZE)
        world_y = int((mouse_y + camera_y) // BLOCK_SIZE)
        
        block_type = world.get_block(world_x, world_y)
        if block_type != BLOCK_AIR:
            world.set_block(world_x, world_y, BLOCK_AIR)
            # Add to inventory
            if block_type in self.inventory:
                self.inventory[block_type] += 1
            else:
                self.inventory[block_type] = 1
            return True
        return False
    
    def place_block(self, world, mouse_x, mouse_y, camera_x, camera_y, block_type):
        """Place block at mouse position"""
        world_x = int((mouse_x + camera_x) // BLOCK_SIZE)
        world_y = int((mouse_y + camera_y) // BLOCK_SIZE)
        
        if world.get_block(world_x, world_y) == BLOCK_AIR:
            if block_type in self.inventory and self.inventory[block_type] > 0:
                world.set_block(world_x, world_y, block_type)
                self.inventory[block_type] -= 1
                if self.inventory[block_type] == 0:
                    del self.inventory[block_type]
                return True
        return False
    
    def draw(self, screen, camera_x, camera_y):
        """Draw player"""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        pygame.draw.rect(screen, RED, (screen_x, screen_y, self.width, self.height))