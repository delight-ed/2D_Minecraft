import pygame
from .constants import *

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
    
    def draw_world(self, world, camera):
        """Draw the world blocks"""
        # Calculate visible block range
        start_x = max(0, int(camera.x // BLOCK_SIZE))
        end_x = min(WORLD_WIDTH, int((camera.x + SCREEN_WIDTH) // BLOCK_SIZE) + 1)
        start_y = max(0, int(camera.y // BLOCK_SIZE))
        end_y = min(WORLD_HEIGHT, int((camera.y + SCREEN_HEIGHT) // BLOCK_SIZE) + 1)
        
        # Draw visible blocks
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                block_type = world.get_block(x, y)
                if block_type != BLOCK_AIR:
                    color = BLOCK_COLORS.get(block_type, WHITE)
                    if color:
                        screen_x = x * BLOCK_SIZE - camera.x
                        screen_y = y * BLOCK_SIZE - camera.y
                        pygame.draw.rect(self.screen, color, 
                                       (screen_x, screen_y, BLOCK_SIZE, BLOCK_SIZE))
                        # Draw block outline
                        pygame.draw.rect(self.screen, BLACK, 
                                       (screen_x, screen_y, BLOCK_SIZE, BLOCK_SIZE), 1)
    
    def draw_ui(self, player):
        """Draw user interface"""
        # Draw inventory
        y_offset = 10
        inventory_text = self.font.render("Inventory:", True, WHITE)
        self.screen.blit(inventory_text, (10, y_offset))
        y_offset += 30
        
        for block_type, count in player.inventory.items():
            block_name = self.get_block_name(block_type)
            text = self.font.render(f"{block_name}: {count}", True, WHITE)
            self.screen.blit(text, (10, y_offset))
            y_offset += 25
        
        # Draw controls
        controls = [
            "Controls:",
            "WASD/Arrow Keys - Move",
            "Space - Jump",
            "Left Click - Mine",
            "Right Click - Place",
            "1-5 - Select Block"
        ]
        
        y_offset = SCREEN_HEIGHT - len(controls) * 25 - 10
        for control in controls:
            text = self.font.render(control, True, WHITE)
            self.screen.blit(text, (10, y_offset))
            y_offset += 25
    
    def get_block_name(self, block_type):
        """Get human-readable block name"""
        names = {
            BLOCK_DIRT: "Dirt",
            BLOCK_GRASS: "Grass",
            BLOCK_STONE: "Stone",
            BLOCK_WATER: "Water",
            BLOCK_SAND: "Sand"
        }
        return names.get(block_type, "Unknown")