import pygame
import math
from src.constants import *
from src.inventory import Inventory

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.health = 100
        self.max_health = 100
        self.hunger = 100
        self.max_hunger = 100
        self.inventory = Inventory()
        self.selected_slot = 0
        self.mining_progress = 0
        self.mining_target = None
        self.reach_distance = 5 * BLOCK_SIZE
        
        # Add starting items
        self.inventory.add_item(ITEM_WOOD_PICKAXE, 1)
        self.inventory.add_item(ITEM_WOOD_SWORD, 1)
        self.inventory.add_item(ITEM_BREAD, 5)
    
    def handle_event(self, event, world):
        if event.type == pygame.KEYDOWN:
            if event.key >= pygame.K_1 and event.key <= pygame.K_9:
                self.selected_slot = event.key - pygame.K_1
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click - mine/attack
                self.start_mining(world)
            elif event.button == 3:  # Right click - place block
                self.place_block(world)
    
    def start_mining(self, world):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Convert screen coordinates to world coordinates
        world_x = int((mouse_x + self.x - SCREEN_WIDTH // 2) // BLOCK_SIZE)
        world_y = int((SCREEN_HEIGHT - mouse_y + self.y) // BLOCK_SIZE)
        
        # Check if target is within reach
        distance = math.sqrt((world_x * BLOCK_SIZE - self.x) ** 2 + (world_y * BLOCK_SIZE - self.y) ** 2)
        if distance <= self.reach_distance:
            self.mining_target = (world_x, world_y)
            self.mining_progress = 0
    
    def place_block(self, world):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_x = int((mouse_x + self.x - SCREEN_WIDTH // 2) // BLOCK_SIZE)
        world_y = int((SCREEN_HEIGHT - mouse_y + self.y) // BLOCK_SIZE)
        
        # Check if target is within reach and not occupied
        distance = math.sqrt((world_x * BLOCK_SIZE - self.x) ** 2 + (world_y * BLOCK_SIZE - self.y) ** 2)
        if distance <= self.reach_distance:
            current_block = world.get_block(world_x, world_y)
            if current_block.type == BLOCK_AIR:
                # Try to place block from inventory
                selected_item = self.inventory.get_selected_item(self.selected_slot)
                if selected_item and self.is_placeable_block(selected_item.item_type):
                    block_type = self.item_to_block_type(selected_item.item_type)
                    world.set_block(world_x, world_y, world.Block(block_type))
                    self.inventory.remove_item(selected_item.item_type, 1)
    
    def is_placeable_block(self, item_type):
        placeable = {
            BLOCK_DIRT, BLOCK_STONE, BLOCK_WOOD, BLOCK_SAND, BLOCK_GRASS
        }
        return item_type in placeable
    
    def item_to_block_type(self, item_type):
        mapping = {
            BLOCK_DIRT: BLOCK_DIRT,
            BLOCK_STONE: BLOCK_STONE,
            BLOCK_WOOD: BLOCK_WOOD,
            BLOCK_SAND: BLOCK_SAND,
            BLOCK_GRASS: BLOCK_GRASS
        }
        return mapping.get(item_type, BLOCK_DIRT)
    
    def update(self, dt, world):
        # Handle input
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx = -PLAYER_SPEED
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx = PLAYER_SPEED
        else:
            self.vx = 0
        
        # Jumping
        if (keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vy = PLAYER_JUMP_SPEED
            self.on_ground = False
        
        # Apply gravity
        self.vy -= GRAVITY * dt
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Collision detection
        self.handle_collisions(world)
        
        # Handle mining
        if self.mining_target:
            mouse_pressed = pygame.mouse.get_pressed()[0]
            if mouse_pressed:
                self.update_mining(world, dt)
            else:
                self.mining_target = None
                self.mining_progress = 0
        
        # Hunger system
        self.hunger -= dt * 0.5
        self.hunger = max(0, self.hunger)
        
        # Health regeneration when well fed
        if self.hunger > 80 and self.health < self.max_health:
            self.health += dt * 2
            self.health = min(self.max_health, self.health)
        
        # Damage from hunger
        elif self.hunger <= 0:
            self.health -= dt * 5
    
    def update_mining(self, world, dt):
        if not self.mining_target:
            return
        
        world_x, world_y = self.mining_target
        block = world.get_block(world_x, world_y)
        
        if block.type == BLOCK_AIR:
            self.mining_target = None
            self.mining_progress = 0
            return
        
        # Calculate mining speed based on tool
        selected_item = self.inventory.get_selected_item(self.selected_slot)
        mining_speed = self.get_mining_speed(selected_item, block.type)
        
        self.mining_progress += mining_speed * dt
        
        if self.mining_progress >= block.hardness:
            # Block broken
            dropped_item = world.break_block(world_x, world_y, mining_speed)
            if dropped_item:
                self.inventory.add_item(dropped_item, 1)
            
            self.mining_target = None
            self.mining_progress = 0
    
    def get_mining_speed(self, tool, block_type):
        base_speed = 1.0
        
        if not tool:
            return base_speed
        
        # Tool effectiveness
        if tool.item_type in [ITEM_WOOD_PICKAXE, ITEM_STONE_PICKAXE, ITEM_IRON_PICKAXE, ITEM_DIAMOND_PICKAXE]:
            if block_type in [BLOCK_STONE, BLOCK_COAL_ORE, BLOCK_IRON_ORE, BLOCK_GOLD_ORE, BLOCK_DIAMOND_ORE]:
                if tool.item_type == ITEM_WOOD_PICKAXE:
                    return base_speed * 2
                elif tool.item_type == ITEM_STONE_PICKAXE:
                    return base_speed * 3
                elif tool.item_type == ITEM_IRON_PICKAXE:
                    return base_speed * 4
                elif tool.item_type == ITEM_DIAMOND_PICKAXE:
                    return base_speed * 6
        
        return base_speed
    
    def handle_collisions(self, world):
        # Get player bounds
        left = int((self.x - PLAYER_WIDTH // 2) // BLOCK_SIZE)
        right = int((self.x + PLAYER_WIDTH // 2) // BLOCK_SIZE)
        bottom = int((self.y - PLAYER_HEIGHT) // BLOCK_SIZE)
        top = int(self.y // BLOCK_SIZE)
        
        # Vertical collision
        self.on_ground = False
        for x in range(left, right + 1):
            # Check bottom collision
            if self.vy <= 0:
                block = world.get_block(x, bottom)
                if block.type != BLOCK_AIR and block.type != BLOCK_WATER:
                    self.y = (bottom + 1) * BLOCK_SIZE + PLAYER_HEIGHT
                    self.vy = 0
                    self.on_ground = True
            
            # Check top collision
            if self.vy > 0:
                block = world.get_block(x, top)
                if block.type != BLOCK_AIR and block.type != BLOCK_WATER:
                    self.y = top * BLOCK_SIZE
                    self.vy = 0
        
        # Horizontal collision
        for y in range(bottom, top + 1):
            # Check left collision
            if self.vx < 0:
                block = world.get_block(left, y)
                if block.type != BLOCK_AIR and block.type != BLOCK_WATER:
                    self.x = (left + 1) * BLOCK_SIZE + PLAYER_WIDTH // 2
            
            # Check right collision
            if self.vx > 0:
                block = world.get_block(right, y)
                if block.type != BLOCK_AIR and block.type != BLOCK_WATER:
                    self.x = right * BLOCK_SIZE - PLAYER_WIDTH // 2
        
        # World boundaries
        self.x = max(PLAYER_WIDTH // 2, min(self.x, WORLD_WIDTH * BLOCK_SIZE - PLAYER_WIDTH // 2))
        self.y = max(PLAYER_HEIGHT, self.y)
    
    def take_damage(self, damage):
        self.health -= damage
        self.health = max(0, self.health)
    
    def heal(self, amount):
        self.health += amount
        self.health = min(self.max_health, self.health)
    
    def eat_food(self, food_value):
        self.hunger += food_value
        self.hunger = min(self.max_hunger, self.hunger)
    
    def render(self, screen, camera):
        screen_x = self.x - camera.x - PLAYER_WIDTH // 2
        screen_y = SCREEN_HEIGHT - (self.y + camera.y)
        
        # Draw player as a simple rectangle
        pygame.draw.rect(screen, BLUE, (screen_x, screen_y - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT))
        pygame.draw.rect(screen, DARK_GRAY, (screen_x, screen_y - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT), 2)
        
        # Draw mining progress
        if self.mining_target and self.mining_progress > 0:
            world_x, world_y = self.mining_target
            progress_x = world_x * BLOCK_SIZE - camera.x
            progress_y = SCREEN_HEIGHT - (world_y + 1) * BLOCK_SIZE + camera.y
            
            # Draw progress bar
            bar_width = BLOCK_SIZE
            bar_height = 4
            progress_width = int(bar_width * (self.mining_progress / world.get_block(world_x, world_y).hardness))
            
            pygame.draw.rect(screen, RED, (progress_x, progress_y - 10, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, (progress_x, progress_y - 10, progress_width, bar_height))