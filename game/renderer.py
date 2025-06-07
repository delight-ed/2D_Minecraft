import pygame
from .constants import *

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
    
    def draw_world(self, world, camera):
        """Draw the world blocks"""
        # Calculate visible block range with some padding
        start_x = max(0, int(camera.x // BLOCK_SIZE) - 1)
        end_x = min(WORLD_WIDTH, int((camera.x + SCREEN_WIDTH) // BLOCK_SIZE) + 2)
        start_y = max(0, int(camera.y // BLOCK_SIZE) - 1)
        end_y = min(WORLD_HEIGHT, int((camera.y + SCREEN_HEIGHT) // BLOCK_SIZE) + 2)
        
        # Draw visible blocks
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                block_type = world.get_block(x, y)
                if block_type != BLOCK_AIR:
                    color = BLOCK_COLORS.get(block_type, WHITE)
                    if color:
                        screen_x = x * BLOCK_SIZE - camera.x
                        screen_y = y * BLOCK_SIZE - camera.y
                        
                        # Only draw if on screen
                        if (-BLOCK_SIZE <= screen_x <= SCREEN_WIDTH and 
                            -BLOCK_SIZE <= screen_y <= SCREEN_HEIGHT):
                            pygame.draw.rect(self.screen, color, 
                                           (screen_x, screen_y, BLOCK_SIZE, BLOCK_SIZE))
                            
                            # Draw block outline for better visibility
                            outline_color = tuple(max(0, c - 30) for c in color)
                            pygame.draw.rect(self.screen, outline_color, 
                                           (screen_x, screen_y, BLOCK_SIZE, BLOCK_SIZE), 1)
        
        # Draw item drops
        self.draw_item_drops(world, camera)
    
    def draw_item_drops(self, world, camera):
        """Draw item drops in the world"""
        for item in world.item_drops:
            screen_x = item['x'] - camera.x
            screen_y = item['y'] - camera.y
            
            # Only draw if on screen
            if (-16 <= screen_x <= SCREEN_WIDTH and -16 <= screen_y <= SCREEN_HEIGHT):
                # Draw item as a smaller colored square
                color = BLOCK_COLORS.get(item['type'], WHITE)
                if color:
                    pygame.draw.rect(self.screen, color, (screen_x - 8, screen_y - 8, 16, 16))
                    pygame.draw.rect(self.screen, BLACK, (screen_x - 8, screen_y - 8, 16, 16), 1)
                    
                    # Add a slight bounce effect
                    bounce = abs((item['time'] % 20) - 10) * 0.5
                    pygame.draw.rect(self.screen, WHITE, 
                                   (screen_x - 6, screen_y - 6 - bounce, 12, 12), 1)
    
    def draw_hotbar(self, player):
        """Draw the hotbar at the bottom of the screen"""
        hotbar_width = HOTBAR_SIZE * HOTBAR_SLOT_SIZE + (HOTBAR_SIZE - 1) * HOTBAR_MARGIN
        hotbar_x = (SCREEN_WIDTH - hotbar_width) // 2
        hotbar_y = SCREEN_HEIGHT - HOTBAR_SLOT_SIZE - 20
        
        for i in range(HOTBAR_SIZE):
            slot_x = hotbar_x + i * (HOTBAR_SLOT_SIZE + HOTBAR_MARGIN)
            slot_y = hotbar_y
            
            # Draw slot background
            if i == player.selected_slot:
                pygame.draw.rect(self.screen, WHITE, 
                               (slot_x - 2, slot_y - 2, HOTBAR_SLOT_SIZE + 4, HOTBAR_SLOT_SIZE + 4))
            
            pygame.draw.rect(self.screen, GRAY, 
                           (slot_x, slot_y, HOTBAR_SLOT_SIZE, HOTBAR_SLOT_SIZE))
            pygame.draw.rect(self.screen, BLACK, 
                           (slot_x, slot_y, HOTBAR_SLOT_SIZE, HOTBAR_SLOT_SIZE), 2)
            
            # Draw block in slot
            if i < len(player.hotbar):
                block_type = player.hotbar[i]
                if block_type != BLOCK_AIR:
                    color = BLOCK_COLORS.get(block_type, WHITE)
                    if color:
                        block_size = HOTBAR_SLOT_SIZE - 10
                        block_x = slot_x + 5
                        block_y = slot_y + 5
                        pygame.draw.rect(self.screen, color, 
                                       (block_x, block_y, block_size, block_size))
                        pygame.draw.rect(self.screen, BLACK, 
                                       (block_x, block_y, block_size, block_size), 1)
                    
                    # Draw count
                    if block_type in player.inventory:
                        count = player.inventory[block_type]
                        if count > 1:
                            count_text = self.small_font.render(str(count), True, WHITE)
                            text_rect = count_text.get_rect()
                            text_rect.bottomright = (slot_x + HOTBAR_SLOT_SIZE - 2, slot_y + HOTBAR_SLOT_SIZE - 2)
                            self.screen.blit(count_text, text_rect)
            
            # Draw slot number
            number_text = self.small_font.render(str(i + 1), True, WHITE)
            self.screen.blit(number_text, (slot_x + 2, slot_y - 18))
    
    def draw_ui(self, player):
        """Draw user interface"""
        # Draw coordinates
        coord_text = self.font.render(f"X: {int(player.x // BLOCK_SIZE)}, Y: {int(player.y // BLOCK_SIZE)}", True, WHITE)
        self.screen.blit(coord_text, (10, 10))
        
        # Draw controls
        controls = [
            "WASD - Move | Space - Jump | E - Inventory",
            "Left Click - Mine | Right Click - Place",
            "1-9 - Select Hotbar Slot"
        ]
        
        for i, control in enumerate(controls):
            text = self.small_font.render(control, True, WHITE)
            self.screen.blit(text, (10, SCREEN_HEIGHT - 80 + i * 20))
        
        # Draw hotbar
        self.draw_hotbar(player)
    
    def get_block_name(self, block_type):
        """Get human-readable block name"""
        names = {
            BLOCK_DIRT: "Dirt",
            BLOCK_GRASS: "Grass",
            BLOCK_STONE: "Stone",
            BLOCK_WATER: "Water",
            BLOCK_SAND: "Sand",
            BLOCK_WOOD: "Wood",
            BLOCK_LEAVES: "Leaves",
            BLOCK_COAL: "Coal",
            BLOCK_IRON: "Iron"
        }
        return names.get(block_type, "Unknown")