import pygame
from .constants import *

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = BLOCK_SIZE - 8
        self.height = BLOCK_SIZE * 2 - 8
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 6
        self.jump_power = 16
        self.gravity = 0.8
        self.on_ground = False
        
        # Empty hotbar - player starts with nothing!
        self.hotbar = [BLOCK_AIR for _ in range(HOTBAR_SIZE)]
        self.selected_slot = 0
        self.inventory = {}
        
        # No starting items - player must gather everything!
    
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
        
        # Keep player in world bounds
        self.x = max(0, min(WORLD_WIDTH * BLOCK_SIZE - self.width, self.x))
    
    def check_collision(self, world, x, y):
        """Check collision with world blocks"""
        # Check corners of player rectangle
        corners = [
            (x + 2, y + 2),
            (x + self.width - 2, y + 2),
            (x + 2, y + self.height - 2),
            (x + self.width - 2, y + self.height - 2)
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
    
    def select_hotbar_slot(self, slot):
        """Select hotbar slot"""
        if 0 <= slot < HOTBAR_SIZE:
            self.selected_slot = slot
    
    def get_selected_block(self):
        """Get currently selected block type"""
        if self.selected_slot < len(self.hotbar):
            return self.hotbar[self.selected_slot]
        return BLOCK_AIR
    
    def add_to_inventory(self, block_type):
        """Add block to inventory and try to put it in hotbar"""
        if block_type in self.inventory:
            self.inventory[block_type] += 1
        else:
            self.inventory[block_type] = 1
        
        # Try to add to hotbar if there's an empty slot
        if block_type not in self.hotbar:
            for i in range(len(self.hotbar)):
                if self.hotbar[i] == BLOCK_AIR:
                    self.hotbar[i] = block_type
                    break
    
    def mine_block(self, world, mouse_x, mouse_y, camera_x, camera_y):
        """Mine block at mouse position"""
        world_x = int((mouse_x + camera_x) // BLOCK_SIZE)
        world_y = int((mouse_y + camera_y) // BLOCK_SIZE)
        
        # Check mining range
        player_center_x = self.x + self.width // 2
        player_center_y = self.y + self.height // 2
        block_center_x = world_x * BLOCK_SIZE + BLOCK_SIZE // 2
        block_center_y = world_y * BLOCK_SIZE + BLOCK_SIZE // 2
        
        distance = ((player_center_x - block_center_x) ** 2 + (player_center_y - block_center_y) ** 2) ** 0.5
        
        if distance > BLOCK_SIZE * 5:  # Mining range limit
            return False
        
        block_type = world.get_block(world_x, world_y)
        if block_type != BLOCK_AIR:
            world.set_block(world_x, world_y, BLOCK_AIR)
            # Add to inventory
            self.add_to_inventory(block_type)
            return True
        return False
    
    def place_block(self, world, mouse_x, mouse_y, camera_x, camera_y):
        """Place block at mouse position"""
        world_x = int((mouse_x + camera_x) // BLOCK_SIZE)
        world_y = int((mouse_y + camera_y) // BLOCK_SIZE)
        
        # Check placement range
        player_center_x = self.x + self.width // 2
        player_center_y = self.y + self.height // 2
        block_center_x = world_x * BLOCK_SIZE + BLOCK_SIZE // 2
        block_center_y = world_y * BLOCK_SIZE + BLOCK_SIZE // 2
        
        distance = ((player_center_x - block_center_x) ** 2 + (player_center_y - block_center_y) ** 2) ** 0.5
        
        if distance > BLOCK_SIZE * 5:  # Placement range limit
            return False
        
        block_type = self.get_selected_block()
        
        if world.get_block(world_x, world_y) == BLOCK_AIR and block_type != BLOCK_AIR:
            if block_type in self.inventory and self.inventory[block_type] > 0:
                # Don't place block inside player
                test_rect = pygame.Rect(world_x * BLOCK_SIZE, world_y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
                
                if not test_rect.colliderect(player_rect):
                    world.set_block(world_x, world_y, block_type)
                    self.inventory[block_type] -= 1
                    if self.inventory[block_type] == 0:
                        del self.inventory[block_type]
                        # Remove from hotbar if count reaches 0
                        for i in range(len(self.hotbar)):
                            if self.hotbar[i] == block_type:
                                self.hotbar[i] = BLOCK_AIR
                                break
                    return True
        return False
    
    def draw(self, screen, camera_x, camera_y):
        """Draw player"""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Only draw if player is on screen
        if (-self.width <= screen_x <= SCREEN_WIDTH and -self.height <= screen_y <= SCREEN_HEIGHT):
            # Draw player body
            pygame.draw.rect(screen, (100, 150, 255), (screen_x, screen_y, self.width, self.height))
            pygame.draw.rect(screen, BLACK, (screen_x, screen_y, self.width, self.height), 2)
            
            # Draw simple face
            eye_size = 3
            pygame.draw.circle(screen, BLACK, (int(screen_x + self.width * 0.3), int(screen_y + 8)), eye_size)
            pygame.draw.circle(screen, BLACK, (int(screen_x + self.width * 0.7), int(screen_y + 8)), eye_size)