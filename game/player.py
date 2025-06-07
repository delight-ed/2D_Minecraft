import pygame
import math
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
        
        # Tools and mining
        self.current_tool = None
        self.can_mine_stone = False
        
        # No starting items - player must gather everything!
    
    def update(self, world):
        """Update player physics and position"""
        # Apply gravity
        self.vel_y += self.gravity
        
        # Limit fall speed
        if self.vel_y > 20:
            self.vel_y = 20
        
        # Move horizontally with better collision
        new_x = self.x + self.vel_x
        if not self.check_collision_horizontal(world, new_x, self.y):
            self.x = new_x
        
        # Move vertically with better collision
        new_y = self.y + self.vel_y
        if self.check_collision_vertical(world, self.x, new_y):
            if self.vel_y > 0:  # Falling
                self.on_ground = True
            self.vel_y = 0
        else:
            self.y = new_y
            self.on_ground = False
        
        # Keep player in world bounds
        self.x = max(0, min(WORLD_WIDTH * BLOCK_SIZE - self.width, self.x))
        
        # Update tool status
        self.update_tool_status()
    
    def check_collision_horizontal(self, world, x, y):
        """Check horizontal collision with better precision"""
        # Check multiple points along the player's height
        check_points = [
            (x + 2, y + 2),                    # Top-left
            (x + self.width - 2, y + 2),       # Top-right
            (x + 2, y + self.height // 2),     # Middle-left
            (x + self.width - 2, y + self.height // 2),  # Middle-right
            (x + 2, y + self.height - 2),      # Bottom-left
            (x + self.width - 2, y + self.height - 2)    # Bottom-right
        ]
        
        for point_x, point_y in check_points:
            block_x = int(point_x // BLOCK_SIZE)
            block_y = int(point_y // BLOCK_SIZE)
            if world.is_solid(block_x, block_y):
                return True
        return False
    
    def check_collision_vertical(self, world, x, y):
        """Check vertical collision with better precision"""
        # Check multiple points along the player's width
        check_points = [
            (x + 2, y + 2),                    # Top-left
            (x + self.width // 2, y + 2),      # Top-center
            (x + self.width - 2, y + 2),       # Top-right
            (x + 2, y + self.height - 2),      # Bottom-left
            (x + self.width // 2, y + self.height - 2),  # Bottom-center
            (x + self.width - 2, y + self.height - 2)    # Bottom-right
        ]
        
        for point_x, point_y in check_points:
            block_x = int(point_x // BLOCK_SIZE)
            block_y = int(point_y // BLOCK_SIZE)
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
    
    def update_tool_status(self):
        """Update what the player can mine based on tools"""
        selected_block = self.get_selected_block()
        
        # Check if player has a pickaxe to mine stone
        self.can_mine_stone = False
        for block_type in self.inventory:
            if block_type == BLOCK_WOOD:  # Wooden pickaxe (we'll add this to crafting)
                self.can_mine_stone = True
                break
    
    def has_line_of_sight(self, world, target_x, target_y):
        """Check if player has clear line of sight to target position"""
        player_center_x = self.x + self.width // 2
        player_center_y = self.y + self.height // 2
        
        # Use Bresenham's line algorithm to check each block along the path
        dx = abs(target_x - player_center_x)
        dy = abs(target_y - player_center_y)
        
        x = int(player_center_x // BLOCK_SIZE)
        y = int(player_center_y // BLOCK_SIZE)
        
        x_inc = 1 if target_x > player_center_x else -1
        y_inc = 1 if target_y > player_center_y else -1
        
        error = dx - dy
        
        target_block_x = int(target_x // BLOCK_SIZE)
        target_block_y = int(target_y // BLOCK_SIZE)
        
        while x != target_block_x or y != target_block_y:
            # Don't check the target block itself
            if world.is_solid(x, y):
                return False
            
            if error > 0:
                x += x_inc
                error -= dy
            else:
                y += y_inc
                error += dx
        
        return True
    
    def can_mine_block(self, block_type):
        """Check if player can mine this block type"""
        if block_type == BLOCK_AIR:
            return False
        
        # Leaves can only be mined with shears (for now, anyone can mine them but they don't drop)
        if block_type == BLOCK_LEAVES:
            return True
        
        # Stone requires a pickaxe
        if block_type in [BLOCK_STONE, BLOCK_COAL, BLOCK_IRON]:
            return self.can_mine_stone
        
        # Other blocks can be mined by hand
        return True
    
    def get_block_drops(self, block_type):
        """Get what items drop when mining a block"""
        # Leaves don't drop anything unless mined with shears
        if block_type == BLOCK_LEAVES:
            return []
        
        # Most blocks drop themselves
        return [block_type]
    
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
        """Mine block at mouse position with line of sight check"""
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
        
        # Check line of sight
        if not self.has_line_of_sight(world, block_center_x, block_center_y):
            return False
        
        block_type = world.get_block(world_x, world_y)
        
        if block_type != BLOCK_AIR and self.can_mine_block(block_type):
            world.set_block(world_x, world_y, BLOCK_AIR)
            
            # Create item drops
            drops = self.get_block_drops(block_type)
            for drop in drops:
                world.add_item_drop(block_center_x, block_center_y, drop)
            
            return True
        return False
    
    def place_block(self, world, mouse_x, mouse_y, camera_x, camera_y):
        """Place block at mouse position with line of sight check"""
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
        
        # Check line of sight (but allow placing adjacent to solid blocks)
        if not self.has_line_of_sight(world, block_center_x, block_center_y):
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
    
    def pickup_items(self, world):
        """Pick up nearby item drops"""
        player_rect = pygame.Rect(self.x - BLOCK_SIZE, self.y - BLOCK_SIZE, 
                                 self.width + BLOCK_SIZE * 2, self.height + BLOCK_SIZE * 2)
        
        for item in world.item_drops[:]:  # Copy list to avoid modification during iteration
            item_rect = pygame.Rect(item['x'] - 8, item['y'] - 8, 16, 16)
            if player_rect.colliderect(item_rect):
                self.add_to_inventory(item['type'])
                world.item_drops.remove(item)
    
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