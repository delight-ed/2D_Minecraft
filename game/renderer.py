import pygame
from .constants import *
from .utils import draw_text_with_shadow, get_block_name

class Renderer:
    def __init__(self, screen, texture_manager):
        self.screen = screen
        self.texture_manager = texture_manager
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
    
    def draw_world(self, world, camera):
        """Draw the world blocks with Minecraft textures"""
        # Calculate visible block range with some padding
        start_x = max(-50, int(camera.x // BLOCK_SIZE) - 1)
        end_x = int((camera.x + SCREEN_WIDTH) // BLOCK_SIZE) + 2
        start_y = max(0, int(camera.y // BLOCK_SIZE) - 1)
        end_y = min(WORLD_HEIGHT, int((camera.y + SCREEN_HEIGHT) // BLOCK_SIZE) + 2)
        
        # Ensure chunks are loaded for visible area
        world.ensure_chunks_loaded(camera.x + SCREEN_WIDTH // 2)
        
        # Draw visible blocks
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                block_type = world.get_block(x, y)
                if block_type != BLOCK_AIR:
                    screen_x = x * BLOCK_SIZE - camera.x
                    screen_y = y * BLOCK_SIZE - camera.y
                    
                    # Only draw if on screen
                    if (-BLOCK_SIZE <= screen_x <= SCREEN_WIDTH and 
                        -BLOCK_SIZE <= screen_y <= SCREEN_HEIGHT):
                        
                        # Draw block with texture
                        self.draw_block_texture(screen_x, screen_y, block_type)
        
        # Draw item drops
        self.draw_item_drops(world, camera)
    
    def draw_block_texture(self, x, y, block_type):
        """Draw block using Minecraft textures"""
        # Get appropriate texture variant for certain blocks
        variant = None
        if block_type == BLOCK_GRASS:
            # Use side texture for grass blocks in 2D view
            variant = "side"
        elif block_type == BLOCK_WOOD:
            # Use side texture for wood logs
            variant = "side"
        
        texture = self.texture_manager.get_texture(block_type, variant)
        
        if texture:
            # Draw the texture
            self.screen.blit(texture, (x, y))
        else:
            # Fallback to color rendering if texture not available
            color = BLOCK_COLORS.get(block_type, (200, 200, 200))
            pygame.draw.rect(self.screen, color, (x, y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.screen, BLACK, (x, y, BLOCK_SIZE, BLOCK_SIZE), 1)
    
    def draw_item_drops(self, world, camera):
        """Draw item drops in the world with textures and stacking"""
        for item in world.item_drops:
            screen_x = item['x'] - camera.x
            screen_y = item['y'] - camera.y
            
            # Only draw if on screen
            if (-20 <= screen_x <= SCREEN_WIDTH and -20 <= screen_y <= SCREEN_HEIGHT):
                # Draw item as a smaller textured square
                item_size = 12
                
                # Get texture for item
                texture = self.texture_manager.get_scaled_texture(item['type'], item_size)
                
                if texture:
                    # Create a surface with alpha for the glow effect
                    glow_surface = pygame.Surface((item_size + 4, item_size + 4), pygame.SRCALPHA)
                    glow_color = (255, 255, 255, 60)  # White glow with transparency
                    pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect())
                    
                    # Draw glow
                    self.screen.blit(glow_surface, 
                                   (screen_x - item_size//2 - 2, screen_y - item_size//2 - 2))
                    
                    # Draw item texture
                    self.screen.blit(texture, 
                                   (screen_x - item_size//2, screen_y - item_size//2))
                else:
                    # Fallback to color rendering
                    if item['type'] in BLOCK_COLORS:
                        color = BLOCK_COLORS[item['type']]
                    elif item['type'] in ITEM_COLORS:
                        color = ITEM_COLORS[item['type']]
                    else:
                        color = (200, 200, 200)
                    
                    if color:
                        pygame.draw.rect(self.screen, color, 
                                       (screen_x - item_size//2, screen_y - item_size//2, item_size, item_size))
                        pygame.draw.rect(self.screen, BLACK, 
                                       (screen_x - item_size//2, screen_y - item_size//2, item_size, item_size), 1)
                
                # Draw stack count if more than 1
                if item['count'] > 1:
                    count_text = self.small_font.render(str(item['count']), True, WHITE)
                    count_rect = count_text.get_rect()
                    count_rect.center = (screen_x + item_size//2 - 4, screen_y + item_size//2 - 4)
                    
                    # Draw background for count
                    bg_rect = count_rect.copy()
                    bg_rect.inflate(2, 2)
                    pygame.draw.rect(self.screen, BLACK, bg_rect)
                    
                    self.screen.blit(count_text, count_rect)
    
    def draw_block_selection(self, player, world, camera, mouse_x, mouse_y):
        """Draw selection outline around block that can be interacted with"""
        world_x, world_y = player.get_block_at_mouse(mouse_x, mouse_y, camera.x, camera.y)
        
        # Check if player can interact with this block
        if player.can_interact_with_block(world, world_x, world_y):
            block_type = world.get_block(world_x, world_y)
            
            # Only show selection if there's a block to mine or empty space to place
            if block_type != BLOCK_AIR or player.get_selected_block() != BLOCK_AIR:
                screen_x = world_x * BLOCK_SIZE - camera.x
                screen_y = world_y * BLOCK_SIZE - camera.y
                
                # Draw selection outline
                selection_color = (255, 255, 255, 100)  # White with transparency
                selection_rect = pygame.Rect(screen_x, screen_y, BLOCK_SIZE, BLOCK_SIZE)
                
                # Create surface for transparent outline
                selection_surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(selection_surface, selection_color, selection_surface.get_rect(), 3)
                
                self.screen.blit(selection_surface, (screen_x, screen_y))
    
    def draw_block_breaking_animation(self, player, camera):
        """Draw block breaking animation"""
        if player.breaking_block is not None:
            world_x, world_y = player.breaking_block
            screen_x = world_x * BLOCK_SIZE - camera.x
            screen_y = world_y * BLOCK_SIZE - camera.y
            
            # Only draw if on screen
            if (-BLOCK_SIZE <= screen_x <= SCREEN_WIDTH and 
                -BLOCK_SIZE <= screen_y <= SCREEN_HEIGHT):
                
                stage = player.get_breaking_animation_stage()
                if stage >= 0:
                    breaking_texture = self.texture_manager.get_breaking_texture(stage)
                    if breaking_texture:
                        self.screen.blit(breaking_texture, (screen_x, screen_y))
    
    def draw_hotbar(self, player):
        """Draw the hotbar at the bottom of the screen with textures"""
        hotbar_width = HOTBAR_SIZE * HOTBAR_SLOT_SIZE + (HOTBAR_SIZE - 1) * HOTBAR_MARGIN
        hotbar_x = (SCREEN_WIDTH - hotbar_width) // 2
        hotbar_y = SCREEN_HEIGHT - HOTBAR_SLOT_SIZE - 20
        
        # Draw hotbar background
        bg_padding = 8
        pygame.draw.rect(self.screen, (40, 40, 40), 
                        (hotbar_x - bg_padding, hotbar_y - bg_padding, 
                         hotbar_width + 2 * bg_padding, HOTBAR_SLOT_SIZE + 2 * bg_padding))
        pygame.draw.rect(self.screen, WHITE, 
                        (hotbar_x - bg_padding, hotbar_y - bg_padding, 
                         hotbar_width + 2 * bg_padding, HOTBAR_SLOT_SIZE + 2 * bg_padding), 2)
        
        for i in range(HOTBAR_SIZE):
            slot_x = hotbar_x + i * (HOTBAR_SLOT_SIZE + HOTBAR_MARGIN)
            slot_y = hotbar_y
            
            # Draw slot background
            if i == player.selected_slot:
                pygame.draw.rect(self.screen, (255, 255, 255, 100), 
                               (slot_x - 3, slot_y - 3, HOTBAR_SLOT_SIZE + 6, HOTBAR_SLOT_SIZE + 6))
                pygame.draw.rect(self.screen, WHITE, 
                               (slot_x - 2, slot_y - 2, HOTBAR_SLOT_SIZE + 4, HOTBAR_SLOT_SIZE + 4), 3)
            
            pygame.draw.rect(self.screen, (80, 80, 80), 
                           (slot_x, slot_y, HOTBAR_SLOT_SIZE, HOTBAR_SLOT_SIZE))
            pygame.draw.rect(self.screen, LIGHT_GRAY, 
                           (slot_x, slot_y, HOTBAR_SLOT_SIZE, HOTBAR_SLOT_SIZE), 2)
            
            # Draw block in slot
            if i < len(player.hotbar):
                block_type = player.hotbar[i]
                if block_type != BLOCK_AIR:
                    icon_size = HOTBAR_SLOT_SIZE - 10
                    icon_x = slot_x + 5
                    icon_y = slot_y + 5
                    
                    # Draw textured icon
                    self.draw_hotbar_icon(icon_x, icon_y, icon_size, block_type)
                    
                    # Draw count
                    if block_type in player.inventory:
                        count = player.inventory[block_type]
                        if count > 1:
                            draw_text_with_shadow(
                                self.screen, self.small_font, str(count),
                                slot_x + HOTBAR_SLOT_SIZE - 15, slot_y + HOTBAR_SLOT_SIZE - 15,
                                WHITE, BLACK
                            )
            
            # Draw slot number
            draw_text_with_shadow(
                self.screen, self.small_font, str(i + 1),
                slot_x + 2, slot_y - 18, WHITE, BLACK
            )
    
    def draw_hotbar_icon(self, x, y, size, item_type):
        """Draw textured icons for hotbar"""
        texture = self.texture_manager.get_scaled_texture(item_type, size)
        
        if texture:
            self.screen.blit(texture, (x, y))
        else:
            # Fallback to color rendering
            if item_type in BLOCK_COLORS:
                color = BLOCK_COLORS[item_type]
            elif item_type in ITEM_COLORS:
                color = ITEM_COLORS[item_type]
            else:
                color = (200, 200, 200)
            
            pygame.draw.rect(self.screen, color, (x, y, size, size))
            pygame.draw.rect(self.screen, BLACK, (x, y, size, size), 1)
    
    def draw_ui(self, player):
        """Draw user interface"""
        # Draw coordinates with background
        coord_text = f"X: {int(player.x // BLOCK_SIZE)}, Y: {int(player.y // BLOCK_SIZE)}"
        
        # Background for coordinates
        coord_rect = draw_text_with_shadow(
            self.screen, self.font, coord_text, 15, 13, WHITE, BLACK
        )
        
        bg_rect = coord_rect.copy()
        bg_rect.x -= 5
        bg_rect.y -= 3
        bg_rect.width += 10
        bg_rect.height += 6
        
        # Draw semi-transparent background
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(150)
        bg_surface.fill((0, 0, 0))
        self.screen.blit(bg_surface, bg_rect)
        pygame.draw.rect(self.screen, WHITE, bg_rect, 1)
        
        # Redraw text on top
        draw_text_with_shadow(self.screen, self.font, coord_text, 15, 13, WHITE, BLACK)
        
        # Draw controls with background
        controls = [
            "WASD - Move | Space - Jump | E - Inventory",
            "Left Click - Mine | Right Click - Place",
            "1-9 - Select Hotbar Slot | ESC - Menu"
        ]
        
        # Calculate background size for controls
        max_width = 0
        total_height = len(controls) * 22 + 10
        
        for control in controls:
            text_width = self.small_font.size(control)[0]
            max_width = max(max_width, text_width)
        
        # Draw controls background
        controls_bg = pygame.Rect(10, SCREEN_HEIGHT - total_height - 10, max_width + 20, total_height)
        bg_surface = pygame.Surface((controls_bg.width, controls_bg.height))
        bg_surface.set_alpha(150)
        bg_surface.fill((0, 0, 0))
        self.screen.blit(bg_surface, controls_bg)
        pygame.draw.rect(self.screen, WHITE, controls_bg, 1)
        
        for i, control in enumerate(controls):
            draw_text_with_shadow(
                self.screen, self.small_font, control,
                20, SCREEN_HEIGHT - total_height + i * 22, WHITE, BLACK
            )
        
        # Draw hotbar
        self.draw_hotbar(player)