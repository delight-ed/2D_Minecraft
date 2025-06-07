import pygame
from .constants import *
from .crafting import CraftingSystem, CRAFTING_RECIPES

class InventoryGUI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.is_open = False
        self.crafting_system = CraftingSystem()
        
        # GUI layout - improved design
        self.slot_size = 45
        self.margin = 3
        self.inventory_rows = 4
        self.inventory_cols = 9
        
        # Calculate positions for centered layout
        total_width = max(
            self.inventory_cols * (self.slot_size + self.margin) + 40,  # Inventory width
            300  # Minimum width for crafting area
        )
        
        self.gui_width = total_width + 40  # Extra padding
        self.gui_height = 500
        self.gui_x = (SCREEN_WIDTH - self.gui_width) // 2
        self.gui_y = (SCREEN_HEIGHT - self.gui_height) // 2
        
        # Crafting area (top section) - 2x2 only
        self.crafting_x = self.gui_x + 20
        self.crafting_y = self.gui_y + 50
        
        # Inventory area (bottom section)
        self.inventory_x = self.gui_x + 20
        self.inventory_y = self.gui_y + 250
        
        # Selected item for moving
        self.selected_item = None
        self.selected_slot = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
    
    def toggle(self):
        """Toggle inventory open/closed"""
        self.is_open = not self.is_open
        if not self.is_open:
            self.selected_item = None
            self.selected_slot = None
    
    def handle_click(self, mouse_x, mouse_y, player):
        """Handle mouse clicks in inventory with improved mechanics"""
        if not self.is_open:
            return False
        
        # Check if click is within GUI bounds
        if not (self.gui_x <= mouse_x <= self.gui_x + self.gui_width and
                self.gui_y <= mouse_y <= self.gui_y + self.gui_height):
            return False
        
        # Get mouse button state
        mouse_buttons = pygame.mouse.get_pressed()
        is_left_click = mouse_buttons[0]
        is_right_click = mouse_buttons[2]
        
        # Check crafting grid clicks (2x2 only)
        for row in range(2):
            for col in range(2):
                slot_x = self.crafting_x + col * (self.slot_size + self.margin)
                slot_y = self.crafting_y + row * (self.slot_size + self.margin)
                
                if (slot_x <= mouse_x <= slot_x + self.slot_size and
                    slot_y <= mouse_y <= slot_y + self.slot_size):
                    self.handle_crafting_click(row, col, player, mouse_x - slot_x, mouse_y - slot_y, is_left_click, is_right_click)
                    return True
        
        # Check crafting result click
        result_x = self.crafting_x + 3 * (self.slot_size + self.margin)
        result_y = self.crafting_y + 0.5 * (self.slot_size + self.margin)
        
        if (result_x <= mouse_x <= result_x + self.slot_size and
            result_y <= mouse_y <= result_y + self.slot_size):
            self.handle_result_click(player, mouse_x - result_x, mouse_y - result_y)
            return True
        
        # Check inventory clicks
        for row in range(self.inventory_rows):
            for col in range(self.inventory_cols):
                slot_x = self.inventory_x + col * (self.slot_size + self.margin)
                slot_y = self.inventory_y + row * (self.slot_size + self.margin)
                
                if (slot_x <= mouse_x <= slot_x + self.slot_size and
                    slot_y <= mouse_y <= slot_y + self.slot_size):
                    self.handle_inventory_click(row, col, player, mouse_x - slot_x, mouse_y - slot_y, is_left_click, is_right_click)
                    return True
        
        # If clicked elsewhere in GUI, drop selected item back to inventory
        if self.selected_item:
            self.return_item_to_inventory(player)
        
        return True
    
    def handle_crafting_click(self, row, col, player, offset_x, offset_y, is_left_click, is_right_click):
        """Handle clicks in crafting grid with improved mechanics"""
        current_item = self.crafting_system.get_item(row, col)
        
        if is_left_click:
            if self.selected_item:
                # Place selected item
                if current_item is None:
                    self.crafting_system.set_item(row, col, self.selected_item[0], self.selected_item[1])
                    self.selected_item = None
                elif current_item[0] == self.selected_item[0]:
                    # Stack items
                    new_count = min(64, current_item[1] + self.selected_item[1])
                    self.crafting_system.set_item(row, col, current_item[0], new_count)
                    remaining = self.selected_item[1] - (new_count - current_item[1])
                    if remaining > 0:
                        self.selected_item = (self.selected_item[0], remaining)
                    else:
                        self.selected_item = None
                else:
                    # Swap items
                    self.crafting_system.set_item(row, col, self.selected_item[0], self.selected_item[1])
                    self.selected_item = current_item
            else:
                # Pick up entire stack
                if current_item:
                    self.selected_item = current_item
                    self.crafting_system.set_item(row, col, None, 0)
                    self.drag_offset_x = offset_x
                    self.drag_offset_y = offset_y
        
        elif is_right_click:
            if self.selected_item:
                # Place one item
                if current_item is None:
                    self.crafting_system.set_item(row, col, self.selected_item[0], 1)
                    if self.selected_item[1] > 1:
                        self.selected_item = (self.selected_item[0], self.selected_item[1] - 1)
                    else:
                        self.selected_item = None
                elif current_item[0] == self.selected_item[0] and current_item[1] < 64:
                    # Add one to stack
                    self.crafting_system.set_item(row, col, current_item[0], current_item[1] + 1)
                    if self.selected_item[1] > 1:
                        self.selected_item = (self.selected_item[0], self.selected_item[1] - 1)
                    else:
                        self.selected_item = None
            else:
                # Pick up half stack
                if current_item and current_item[1] > 1:
                    half = current_item[1] // 2
                    remaining = current_item[1] - half
                    self.selected_item = (current_item[0], half)
                    self.crafting_system.set_item(row, col, current_item[0], remaining)
                    self.drag_offset_x = offset_x
                    self.drag_offset_y = offset_y
                elif current_item:
                    # Pick up single item
                    self.selected_item = current_item
                    self.crafting_system.set_item(row, col, None, 0)
                    self.drag_offset_x = offset_x
                    self.drag_offset_y = offset_y
    
    def handle_result_click(self, player, offset_x, offset_y):
        """Handle clicks on crafting result"""
        # Check if there's a valid result and no item currently selected
        if self.crafting_system.result and not self.selected_item:
            result_item, result_count = self.crafting_system.result
            
            # Check if we can craft (have ingredients in inventory)
            recipe_data = CRAFTING_RECIPES.get(result_item)
            if recipe_data:
                can_craft = True
                for req_item, req_count in recipe_data['ingredients']:
                    # Check if we have enough items in the crafting grid
                    grid_count = 0
                    for i in range(2):
                        for j in range(2):
                            item = self.crafting_system.get_item(i, j)
                            if item and item[0] == req_item:
                                grid_count += item[1]
                    
                    if grid_count < req_count:
                        can_craft = False
                        break
                
                if can_craft:
                    # Remove ingredients from crafting grid
                    for req_item, req_count in recipe_data['ingredients']:
                        remaining_to_remove = req_count
                        for i in range(2):
                            for j in range(2):
                                if remaining_to_remove <= 0:
                                    break
                                item = self.crafting_system.get_item(i, j)
                                if item and item[0] == req_item:
                                    remove_count = min(remaining_to_remove, item[1])
                                    new_count = item[1] - remove_count
                                    remaining_to_remove -= remove_count
                                    
                                    if new_count > 0:
                                        self.crafting_system.set_item(i, j, item[0], new_count)
                                    else:
                                        self.crafting_system.set_item(i, j, None, 0)
                    
                    # Pick up the result
                    self.selected_item = (result_item, result_count)
                    self.drag_offset_x = offset_x
                    self.drag_offset_y = offset_y
                    
                    # Update the crafting result after removing ingredients
                    self.crafting_system.update_result()
    
    def handle_inventory_click(self, row, col, player, offset_x, offset_y, is_left_click, is_right_click):
        """Handle clicks in inventory grid with improved mechanics"""
        # Convert inventory dict to list for grid display
        inventory_items = list(player.inventory.items())
        slot_index = row * self.inventory_cols + col
        
        if is_left_click:
            if self.selected_item:
                # Place selected item in inventory
                if slot_index < len(inventory_items):
                    item_type, count = inventory_items[slot_index]
                    if item_type == self.selected_item[0]:
                        # Stack items
                        new_count = min(64, count + self.selected_item[1])
                        added = new_count - count
                        player.inventory[item_type] = new_count
                        if self.selected_item[1] > added:
                            self.selected_item = (self.selected_item[0], self.selected_item[1] - added)
                        else:
                            self.selected_item = None
                    else:
                        # Swap items
                        del player.inventory[item_type]
                        player.inventory[self.selected_item[0]] = self.selected_item[1]
                        self.selected_item = (item_type, count)
                        self.drag_offset_x = offset_x
                        self.drag_offset_y = offset_y
                else:
                    # Add new item to inventory
                    player.inventory[self.selected_item[0]] = self.selected_item[1]
                    self.selected_item = None
            else:
                # Pick up entire stack from inventory
                if slot_index < len(inventory_items):
                    item_type, count = inventory_items[slot_index]
                    self.selected_item = (item_type, count)
                    del player.inventory[item_type]
                    self.drag_offset_x = offset_x
                    self.drag_offset_y = offset_y
        
        elif is_right_click:
            if self.selected_item:
                # Place one item
                if slot_index < len(inventory_items):
                    item_type, count = inventory_items[slot_index]
                    if item_type == self.selected_item[0] and count < 64:
                        # Add one to existing stack
                        player.inventory[item_type] = count + 1
                        if self.selected_item[1] > 1:
                            self.selected_item = (self.selected_item[0], self.selected_item[1] - 1)
                        else:
                            self.selected_item = None
                else:
                    # Place one item in empty slot
                    player.inventory[self.selected_item[0]] = 1
                    if self.selected_item[1] > 1:
                        self.selected_item = (self.selected_item[0], self.selected_item[1] - 1)
                    else:
                        self.selected_item = None
            else:
                # Pick up half stack
                if slot_index < len(inventory_items):
                    item_type, count = inventory_items[slot_index]
                    if count > 1:
                        half = count // 2
                        remaining = count - half
                        self.selected_item = (item_type, half)
                        player.inventory[item_type] = remaining
                        self.drag_offset_x = offset_x
                        self.drag_offset_y = offset_y
                    else:
                        # Pick up single item
                        self.selected_item = (item_type, count)
                        del player.inventory[item_type]
                        self.drag_offset_x = offset_x
                        self.drag_offset_y = offset_y
    
    def return_item_to_inventory(self, player):
        """Return selected item to player inventory"""
        if self.selected_item:
            item_type, count = self.selected_item
            if item_type in player.inventory:
                player.inventory[item_type] += count
            else:
                player.inventory[item_type] = count
            self.selected_item = None
    
    def draw(self, player):
        """Draw the inventory GUI"""
        if not self.is_open:
            return
        
        # Draw background with gradient
        background_rect = pygame.Rect(self.gui_x, self.gui_y, self.gui_width, self.gui_height)
        
        # Gradient background
        for y in range(self.gui_height):
            color_value = 80 + int((y / self.gui_height) * 40)
            color = (color_value, color_value, color_value)
            pygame.draw.line(self.screen, color, 
                           (self.gui_x, self.gui_y + y), 
                           (self.gui_x + self.gui_width, self.gui_y + y))
        
        # Border
        pygame.draw.rect(self.screen, WHITE, background_rect, 3)
        pygame.draw.rect(self.screen, BLACK, background_rect, 1)
        
        # Title
        title_text = self.font.render("Inventory & Crafting", True, WHITE)
        title_rect = title_text.get_rect(center=(self.gui_x + self.gui_width // 2, self.gui_y + 25))
        self.screen.blit(title_text, title_rect)
        
        # Draw crafting section
        self.draw_crafting_section()
        
        # Draw inventory section
        self.draw_inventory_section(player)
        
        # Draw selected item following mouse
        if self.selected_item:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.draw_item_icon(mouse_x - self.drag_offset_x, mouse_y - self.drag_offset_y, 
                              self.selected_item[0], self.selected_item[1], alpha=200)
    
    def draw_crafting_section(self):
        """Draw the crafting section (2x2 only)"""
        # Section background
        section_rect = pygame.Rect(self.crafting_x - 10, self.crafting_y - 30, 
                                 self.gui_width - 40, 180)
        pygame.draw.rect(self.screen, (60, 60, 60), section_rect)
        pygame.draw.rect(self.screen, LIGHT_GRAY, section_rect, 2)
        
        # Title
        title = self.small_font.render("Crafting (2x2)", True, WHITE)
        self.screen.blit(title, (self.crafting_x, self.crafting_y - 25))
        
        # Draw 2x2 crafting grid
        for row in range(2):
            for col in range(2):
                slot_x = self.crafting_x + col * (self.slot_size + self.margin)
                slot_y = self.crafting_y + row * (self.slot_size + self.margin)
                
                # Draw slot
                pygame.draw.rect(self.screen, (100, 100, 100), 
                               (slot_x, slot_y, self.slot_size, self.slot_size))
                pygame.draw.rect(self.screen, WHITE, 
                               (slot_x, slot_y, self.slot_size, self.slot_size), 2)
                
                # Draw item in slot
                item = self.crafting_system.get_item(row, col)
                if item:
                    self.draw_item_icon(slot_x + 2, slot_y + 2, item[0], item[1])
        
        # Draw arrow
        arrow_x = self.crafting_x + 2.5 * (self.slot_size + self.margin)
        arrow_y = self.crafting_y + 0.5 * (self.slot_size + self.margin) + self.slot_size // 2
        
        # Arrow background
        pygame.draw.circle(self.screen, (80, 80, 80), (int(arrow_x + 10), int(arrow_y)), 15)
        pygame.draw.circle(self.screen, WHITE, (int(arrow_x + 10), int(arrow_y)), 15, 2)
        
        # Arrow shape
        pygame.draw.polygon(self.screen, WHITE, [
            (arrow_x, arrow_y - 6),
            (arrow_x, arrow_y + 6),
            (arrow_x + 20, arrow_y)
        ])
        
        # Draw result slot
        result_x = self.crafting_x + 3 * (self.slot_size + self.margin)
        result_y = self.crafting_y + 0.5 * (self.slot_size + self.margin)
        
        pygame.draw.rect(self.screen, (120, 120, 120), 
                        (result_x, result_y, self.slot_size, self.slot_size))
        pygame.draw.rect(self.screen, YELLOW, 
                        (result_x, result_y, self.slot_size, self.slot_size), 3)
        
        # Draw result
        if self.crafting_system.result:
            result_item, result_count = self.crafting_system.result
            self.draw_item_icon(result_x + 2, result_y + 2, result_item, result_count)
    
    def draw_inventory_section(self, player):
        """Draw the inventory section"""
        # Section background
        section_rect = pygame.Rect(self.inventory_x - 10, self.inventory_y - 30, 
                                 self.gui_width - 40, 220)
        pygame.draw.rect(self.screen, (60, 60, 60), section_rect)
        pygame.draw.rect(self.screen, LIGHT_GRAY, section_rect, 2)
        
        # Title
        title = self.small_font.render("Inventory", True, WHITE)
        self.screen.blit(title, (self.inventory_x, self.inventory_y - 25))
        
        # Convert inventory to list for grid display
        inventory_items = list(player.inventory.items())
        
        for row in range(self.inventory_rows):
            for col in range(self.inventory_cols):
                slot_x = self.inventory_x + col * (self.slot_size + self.margin)
                slot_y = self.inventory_y + row * (self.slot_size + self.margin)
                
                # Draw slot
                pygame.draw.rect(self.screen, (100, 100, 100), 
                               (slot_x, slot_y, self.slot_size, self.slot_size))
                pygame.draw.rect(self.screen, WHITE, 
                               (slot_x, slot_y, self.slot_size, self.slot_size), 2)
                
                # Draw item in slot
                slot_index = row * self.inventory_cols + col
                if slot_index < len(inventory_items):
                    item_type, count = inventory_items[slot_index]
                    self.draw_item_icon(slot_x + 2, slot_y + 2, item_type, count)
    
    def draw_item_icon(self, x, y, item_type, count, alpha=255):
        """Draw an item icon with count and 8-bit textures"""
        icon_size = self.slot_size - 4
        
        # Create surface for alpha blending
        icon_surface = pygame.Surface((icon_size, icon_size))
        icon_surface.set_alpha(alpha)
        
        # Get color for item
        if item_type in BLOCK_COLORS:
            color = BLOCK_COLORS[item_type]
        elif item_type in ITEM_COLORS:
            color = ITEM_COLORS[item_type]
        else:
            color = (200, 200, 200)  # Default gray
        
        if color:
            # Draw 8-bit style texture
            self.draw_8bit_texture(icon_surface, item_type, icon_size)
        
        self.screen.blit(icon_surface, (x, y))
        
        # Draw count
        if count > 1:
            count_text = self.small_font.render(str(count), True, WHITE)
            count_surface = pygame.Surface(count_text.get_size())
            count_surface.fill(BLACK)
            count_surface.blit(count_text, (0, 0))
            count_surface.set_alpha(alpha)
            
            text_rect = count_surface.get_rect()
            text_rect.bottomright = (x + icon_size - 2, y + icon_size - 2)
            self.screen.blit(count_surface, text_rect)
    
    def draw_8bit_texture(self, surface, item_type, size):
        """Draw 8-bit style textures for items"""
        if item_type == BLOCK_GRASS:
            # Grass block - green top, brown sides
            surface.fill((101, 67, 33))  # Brown base
            pygame.draw.rect(surface, (34, 139, 34), (0, 0, size, size // 3))  # Green top
            # Add some texture lines
            for i in range(2, size, 4):
                pygame.draw.line(surface, (20, 100, 20), (i, 0), (i, size // 3))
        
        elif item_type == BLOCK_DIRT:
            # Dirt texture
            surface.fill((101, 67, 33))
            # Add dirt spots
            for i in range(4, size, 8):
                for j in range(4, size, 8):
                    pygame.draw.rect(surface, (80, 50, 25), (i, j, 3, 3))
        
        elif item_type == BLOCK_STONE:
            # Stone texture
            surface.fill((105, 105, 105))
            # Add stone pattern
            for i in range(2, size, 6):
                for j in range(2, size, 6):
                    pygame.draw.rect(surface, (85, 85, 85), (i, j, 2, 2))
        
        elif item_type == BLOCK_WOOD:
            # Wood texture
            surface.fill((139, 90, 43))
            # Add wood grain
            for i in range(0, size, 2):
                pygame.draw.line(surface, (120, 75, 35), (0, i), (size, i))
        
        elif item_type == BLOCK_LEAVES:
            # Leaves texture
            surface.fill((0, 100, 0))
            # Add leaf pattern
            for i in range(1, size, 4):
                for j in range(1, size, 4):
                    if (i + j) % 8 < 4:
                        pygame.draw.rect(surface, (0, 120, 0), (i, j, 2, 2))
        
        elif item_type == ITEM_STICK:
            # Stick texture - vertical brown rectangle
            surface.fill((0, 0, 0, 0))  # Transparent background
            stick_width = size // 4
            stick_x = (size - stick_width) // 2
            pygame.draw.rect(surface, (139, 90, 43), (stick_x, 2, stick_width, size - 4))
            pygame.draw.rect(surface, (100, 65, 30), (stick_x, 2, 1, size - 4))  # Shadow
        
        elif item_type == ITEM_CRAFTING_TABLE:
            # Crafting table texture
            surface.fill((160, 82, 45))
            # Add crafting table pattern
            pygame.draw.rect(surface, (180, 100, 60), (2, 2, size - 4, size - 4))
            pygame.draw.line(surface, (100, 50, 25), (size//2, 2), (size//2, size - 2))
            pygame.draw.line(surface, (100, 50, 25), (2, size//2), (size - 2, size//2))
        
        elif item_type == ITEM_WOODEN_PICKAXE:
            # Wooden pickaxe texture
            surface.fill((0, 0, 0, 0))  # Transparent background
            # Handle
            handle_width = size // 6
            handle_x = (size - handle_width) // 2
            pygame.draw.rect(surface, (139, 90, 43), (handle_x, size//2, handle_width, size//2))
            # Pickaxe head
            head_height = size // 3
            pygame.draw.rect(surface, (120, 75, 35), (2, size//4, size - 4, head_height))
            # Pickaxe points
            pygame.draw.polygon(surface, (100, 65, 30), [
                (2, size//4 + head_height//2),
                (0, size//4 + head_height//2 - 3),
                (0, size//4 + head_height//2 + 3)
            ])
            pygame.draw.polygon(surface, (100, 65, 30), [
                (size - 2, size//4 + head_height//2),
                (size, size//4 + head_height//2 - 3),
                (size, size//4 + head_height//2 + 3)
            ])
        
        else:
            # Default texture for unknown items
            if item_type in BLOCK_COLORS:
                color = BLOCK_COLORS[item_type]
            elif item_type in ITEM_COLORS:
                color = ITEM_COLORS[item_type]
            else:
                color = (200, 200, 200)
            
            surface.fill(color)
        
        # Add border
        pygame.draw.rect(surface, BLACK, (0, 0, size, size), 1)