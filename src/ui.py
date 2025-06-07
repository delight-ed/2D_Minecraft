import pygame
from src.constants import *

class UI:
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.inventory_open = False
        self.crafting_open = False
    
    def handle_event(self, event, state):
        self.inventory_open = (state == STATE_INVENTORY)
        self.crafting_open = (state == STATE_CRAFTING)
    
    def update(self, dt, player):
        pass
    
    def render(self, screen, player, state):
        # Render HUD
        self.render_hud(screen, player)
        
        # Render inventory if open
        if state == STATE_INVENTORY:
            self.render_inventory(screen, player)
        
        # Render crafting if open
        if state == STATE_CRAFTING:
            self.render_crafting(screen, player)
    
    def render_hud(self, screen, player):
        # Health bar
        health_width = 200
        health_height = 20
        health_ratio = player.health / player.max_health
        
        pygame.draw.rect(screen, RED, (20, 20, health_width, health_height))
        pygame.draw.rect(screen, GREEN, (20, 20, health_width * health_ratio, health_height))
        pygame.draw.rect(screen, BLACK, (20, 20, health_width, health_height), 2)
        
        health_text = self.font.render(f"Health: {int(player.health)}/{player.max_health}", True, WHITE)
        screen.blit(health_text, (25, 22))
        
        # Hunger bar
        hunger_width = 200
        hunger_height = 20
        hunger_ratio = player.hunger / player.max_hunger
        
        pygame.draw.rect(screen, BROWN, (20, 50, hunger_width, hunger_height))
        pygame.draw.rect(screen, ORANGE, (20, 50, hunger_width * hunger_ratio, hunger_height))
        pygame.draw.rect(screen, BLACK, (20, 50, hunger_width, hunger_height), 2)
        
        hunger_text = self.font.render(f"Hunger: {int(player.hunger)}/{player.max_hunger}", True, WHITE)
        screen.blit(hunger_text, (25, 52))
        
        # Hotbar
        self.render_hotbar(screen, player)
        
        # Instructions
        instructions = [
            "WASD/Arrow Keys: Move",
            "Space: Jump",
            "Mouse: Mine/Place blocks",
            "1-9: Select hotbar slot",
            "E: Inventory",
            "C: Crafting"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH - 200, 20 + i * 20))
    
    def render_hotbar(self, screen, player):
        hotbar_slots = 9
        slot_size = 40
        hotbar_width = hotbar_slots * slot_size
        hotbar_x = (SCREEN_WIDTH - hotbar_width) // 2
        hotbar_y = SCREEN_HEIGHT - 60
        
        # Draw hotbar background
        pygame.draw.rect(screen, DARK_GRAY, (hotbar_x - 5, hotbar_y - 5, hotbar_width + 10, slot_size + 10))
        
        # Draw slots
        items_list = list(player.inventory.items.values())
        for i in range(hotbar_slots):
            slot_x = hotbar_x + i * slot_size
            slot_color = YELLOW if i == player.selected_slot else WHITE
            
            pygame.draw.rect(screen, slot_color, (slot_x, hotbar_y, slot_size, slot_size), 2)
            
            # Draw item if present
            if i < len(items_list):
                item = items_list[i]
                item_color = self.get_item_display_color(item.item_type)
                pygame.draw.rect(screen, item_color, (slot_x + 5, hotbar_y + 5, slot_size - 10, slot_size - 10))
                
                # Draw quantity
                if item.quantity > 1:
                    qty_text = self.small_font.render(str(item.quantity), True, WHITE)
                    screen.blit(qty_text, (slot_x + slot_size - 15, hotbar_y + slot_size - 15))
    
    def render_inventory(self, screen, player):
        # Draw inventory background
        inv_width = 400
        inv_height = 300
        inv_x = (SCREEN_WIDTH - inv_width) // 2
        inv_y = (SCREEN_HEIGHT - inv_height) // 2
        
        pygame.draw.rect(screen, DARK_GRAY, (inv_x, inv_y, inv_width, inv_height))
        pygame.draw.rect(screen, WHITE, (inv_x, inv_y, inv_width, inv_height), 3)
        
        # Title
        title = self.font.render("Inventory", True, WHITE)
        screen.blit(title, (inv_x + 10, inv_y + 10))
        
        # Draw items
        y_offset = 50
        for item_type, item in player.inventory.items.items():
            item_name = player.inventory.get_item_name(item_type)
            item_text = f"{item_name} x{item.quantity}"
            
            text_surface = self.small_font.render(item_text, True, WHITE)
            screen.blit(text_surface, (inv_x + 20, inv_y + y_offset))
            
            # Draw item color indicator
            item_color = self.get_item_display_color(item_type)
            pygame.draw.rect(screen, item_color, (inv_x + inv_width - 40, inv_y + y_offset, 20, 15))
            
            y_offset += 25
            if y_offset > inv_height - 50:
                break
        
        # Instructions
        close_text = self.small_font.render("Press E to close", True, WHITE)
        screen.blit(close_text, (inv_x + 10, inv_y + inv_height - 25))
    
    def render_crafting(self, screen, player):
        # Draw crafting background
        craft_width = 500
        craft_height = 400
        craft_x = (SCREEN_WIDTH - craft_width) // 2
        craft_y = (SCREEN_HEIGHT - craft_height) // 2
        
        pygame.draw.rect(screen, DARK_GRAY, (craft_x, craft_y, craft_width, craft_height))
        pygame.draw.rect(screen, WHITE, (craft_x, craft_y, craft_width, craft_height), 3)
        
        # Title
        title = self.font.render("Crafting", True, WHITE)
        screen.blit(title, (craft_x + 10, craft_y + 10))
        
        # Simple crafting recipes display
        recipes = [
            "Wood Pickaxe: 3 Wood + 2 Sticks",
            "Stone Pickaxe: 3 Stone + 2 Sticks",
            "Iron Pickaxe: 3 Iron + 2 Sticks",
            "Wood Sword: 2 Wood + 1 Stick",
            "Stone Sword: 2 Stone + 1 Stick",
            "Bread: 3 Wheat",
        ]
        
        y_offset = 50
        for recipe in recipes:
            recipe_text = self.small_font.render(recipe, True, WHITE)
            screen.blit(recipe_text, (craft_x + 20, craft_y + y_offset))
            y_offset += 25
        
        # Instructions
        close_text = self.small_font.render("Press C to close", True, WHITE)
        screen.blit(close_text, (craft_x + 10, craft_y + craft_height - 25))
        
        note_text = self.small_font.render("(Crafting system simplified for demo)", True, YELLOW)
        screen.blit(note_text, (craft_x + 10, craft_y + craft_height - 50))
    
    def get_item_display_color(self, item_type):
        # Similar to item manager colors but for UI display
        if item_type < 100:  # Block items
            colors = {
                BLOCK_GRASS: GREEN,
                BLOCK_DIRT: BROWN,
                BLOCK_STONE: GRAY,
                BLOCK_WOOD: (101, 67, 33),
                BLOCK_SAND: (238, 203, 173),
                BLOCK_COAL_ORE: BLACK,
                BLOCK_IRON_ORE: (205, 127, 50),
                BLOCK_GOLD_ORE: YELLOW,
                BLOCK_DIAMOND_ORE: (185, 242, 255),
            }
            return colors.get(item_type, WHITE)
        else:  # Tools and items
            colors = {
                ITEM_WOOD_PICKAXE: BROWN,
                ITEM_STONE_PICKAXE: GRAY,
                ITEM_IRON_PICKAXE: (192, 192, 192),
                ITEM_DIAMOND_PICKAXE: (185, 242, 255),
                ITEM_WOOD_SWORD: BROWN,
                ITEM_STONE_SWORD: GRAY,
                ITEM_IRON_SWORD: (192, 192, 192),
                ITEM_DIAMOND_SWORD: (185, 242, 255),
                ITEM_BREAD: (222, 184, 135),
                ITEM_APPLE: RED,
                ITEM_COAL: BLACK,
                ITEM_IRON_INGOT: (192, 192, 192),
                ITEM_GOLD_INGOT: YELLOW,
                ITEM_DIAMOND: (185, 242, 255)
            }
            return colors.get(item_type, WHITE)