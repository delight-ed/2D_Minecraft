import pygame
import random
import math
from src.constants import *

class DroppedItem:
    def __init__(self, item_type, x, y, quantity=1):
        self.item_type = item_type
        self.x = x
        self.y = y
        self.quantity = quantity
        self.vx = random.uniform(-50, 50)
        self.vy = random.uniform(100, 200)
        self.lifetime = 300  # 5 minutes
        self.pickup_delay = 1.0  # Can't be picked up immediately
    
    def update(self, dt):
        self.lifetime -= dt
        self.pickup_delay -= dt
        
        # Simple physics
        self.vy -= GRAVITY * dt * 0.5  # Less gravity for items
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Friction
        self.vx *= 0.98
        
        # Ground collision (simplified)
        if self.y < 50:
            self.y = 50
            self.vy = 0
            self.vx *= 0.8
    
    def can_pickup(self):
        return self.pickup_delay <= 0
    
    def is_expired(self):
        return self.lifetime <= 0

class ItemManager:
    def __init__(self):
        self.dropped_items = []
    
    def drop_item(self, item_type, x, y, quantity=1):
        item = DroppedItem(item_type, x, y, quantity)
        self.dropped_items.append(item)
    
    def update(self, dt, player):
        for item in self.dropped_items[:]:
            item.update(dt)
            
            # Check for pickup
            if item.can_pickup():
                distance = math.sqrt((player.x - item.x) ** 2 + (player.y - item.y) ** 2)
                if distance < 40:  # Pickup range
                    player.inventory.add_item(item.item_type, item.quantity)
                    self.dropped_items.remove(item)
                    continue
            
            # Remove expired items
            if item.is_expired():
                self.dropped_items.remove(item)
    
    def render(self, screen, camera):
        for item in self.dropped_items:
            screen_x = item.x - camera.x - 8
            screen_y = SCREEN_HEIGHT - (item.y + camera.y) - 8
            
            # Draw item as a small colored square
            color = self.get_item_color(item.item_type)
            pygame.draw.rect(screen, color, (screen_x, screen_y, 16, 16))
            pygame.draw.rect(screen, BLACK, (screen_x, screen_y, 16, 16), 1)
    
    def get_item_color(self, item_type):
        # Use similar colors as blocks
        if item_type < 100:  # Block items
            from src.world import World
            world = World()
            return world.get_block_color(item_type)
        else:  # Tool/food items
            colors = {
                ITEM_WOOD_PICKAXE: BROWN,
                ITEM_STONE_PICKAXE: GRAY,
                ITEM_IRON_PICKAXE: (192, 192, 192),
                ITEM_DIAMOND_PICKAXE: (185, 242, 255),
                ITEM_BREAD: (222, 184, 135),
                ITEM_APPLE: RED,
                ITEM_COAL: BLACK,
                ITEM_IRON_INGOT: (192, 192, 192),
                ITEM_GOLD_INGOT: YELLOW,
                ITEM_DIAMOND: (185, 242, 255)
            }
            return colors.get(item_type, WHITE)