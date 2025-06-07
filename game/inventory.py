import pygame
from .constants import *
from .crafting import CraftingSystem

class InventoryGUI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.is_open = False
        self.crafting_system = CraftingSystem()
        
        # GUI layout
        self.slot_size = 40
        self.margin = 5
        self.inventory_rows = 4
        self.inventory_cols = 9
        
        # Calculate positions
        self.gui_width = self.inventory_cols * (self.slot_size + self.margin) + 200
        self.gui_height = self.inventory_rows * (self.slot_size + self.margin) + 200
        self.gui_x = (SCREEN_WIDTH - self.gui_width) // 2
        self.gui_y = (SCREEN_HEIGHT - self.gui_height) // 2
        
        # Crafting area
        self.crafting_x = self.gui_x + 20
        self.crafting_y = self.gui_y + 20
        
        # Inventory area
        self.inventory_x = self.gui_x + 200
        self.inventory_y = self.gui_y + 20
        
        # Selected item for moving
        self.selected_item = None
        self.selected_slot = None
    
    def toggle(self):
        """Toggle inventory open/closed"""
        self.is_open = not self.is_open
        if not self.is_open:
            self.selected_item = None
            self.selected_slot = None
    
    def handle_click(self, mouse_x, mouse_y, player):
        """Handle mouse clicks in inventory"""
        if not self.is_open:
            return False
        
        # Check crafting grid clicks
        for row in range(3):
            for col in range(3):
                slot_x = self.crafting_x + col * (self.slot_size + self.margin)
                slot_y = self.crafting_y + row * (self.slot_size + self.margin)
                
                if (slot_x <= mouse_x <= slot_x + self.slot_size and
                    slot_y <= mouse_y <= slot_y + self.slot_size):
                    self.handle_crafting_click(row, col, player)
                    return True
        
        # Check crafting result click
        result_x = self.crafting_x + 4 * (self.slot_size + self.margin)
        result_y = self.crafting_y + 1 * (self.slot_size + self.margin)
        
        if (result_x <= mouse_x <= result_x + self.slot_size and
            result_y <= mouse_y <= result_y + self.slot_size):
            self.handle_result_click(player)
            return True
        
        # Check inventory clicks
        for row in range(self.inventory_rows):
            for col in range(self.inventory_cols):
                slot_x = self.inventory_x + col * (self.slot_size + self.margin)
                slot_y = self.inventory_y + row * (self.slot_size + self.margin)
                
                if (slot_x <= mouse_x <= slot_x + self.slot_size and
                    slot_y <= mouse_y <= slot_y + self.slot_size):
                    self.handle_inventory_click(row, col, player)
                    return True
        
        return False
    
    def handle_crafting_click(self, row, col, player):
        """Handle clicks in crafting grid"""
        current_item = self.crafting_system.get_item(row, col)
        
        if self.selected_item:
            # Place selected item
            if current_item is None:
                self.crafting_system.set_item(row, col, self.selected_item[0], 1)
                if self.selected_item[1] > 1:
                    self.selected_item = (self.selected_item[0], self.selected_item[1] - 1)
                else:
                    self.selected_item = None
            elif current_item[0] == self.selected_item[0]:
                # Stack items
                new_count = min(64, current_item[1] + 1)
                self.crafting_system.set_item(row, col, current_item[0], new_count)
                if new_count > current_item[1]:
                    if self.selected_item[1] > 1:
                        self.selected_item = (self.selected_item[0], self.selected_item[1] - 1)
                    else:
                        self.selected_item = None
        else:
            # Pick up item
            if current_item:
                self.selected_item = current_item
                self.crafting_system.set_item(row, col, None, 0)
    
    def handle_result_click(self, player):
        """Handle clicks on crafting result"""
        if self.crafting_system.result and not self.selected_item:
            if self.crafting_system.craft_item(player.inventory):
                # Successfully crafted
                result_item, result_count = self.crafting_system.result
                self.selected_item = (result_item, result_count)
    
    def handle_inventory_click(self, row, col, player):
        """Handle clicks in inventory grid"""
        # Convert inventory dict to list for grid display
        inventory_items = list(player.inventory.items())
        slot_index = row * self.inventory_cols + col
        
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
                # Add new item to inventory
                if self.selected_item[0] in player.inventory:
                    player.inventory[self.selected_item[0]] += self.selected_item[1]
                else:
                    player.inventory[self.selected_item[0]] = self.selected_item[1]
                self.selected_item = None
        else:
            # Pick up item from inventory
            if slot_index < len(inventory_items):
                item_type, count = inventory_items[slot_index]
                self.selected_item = (item_type, count)
                del player.inventory[item_type]
    
    def draw(self, player):
        """Draw the inventory GUI"""
        if not self.is_open:
            return
        
        # Draw background
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (self.gui_x, self.gui_y, self.gui_width, self.gui_height))
        pygame.draw.rect(self.screen, BLACK, 
                        (self.gui_x, self.gui_y, self.gui_width, self.gui_height), 3)
        
        # Draw title
        title = self.font.render("Inventory & Crafting", True, WHITE)
        self.screen.blit(title, (self.gui_x + 10, self.gui_y + 5))
        
        # Draw crafting grid
        self.draw_crafting_grid()
        
        # Draw inventory grid
        self.draw_inventory_grid(player)
        
        # Draw selected item following mouse
        if self.selected_item:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.draw_item_icon(mouse_x - 20, mouse_y - 20, self.selected_item[0], self.selected_item[1])
    
    def draw_crafting_grid(self):
        """Draw the crafting grid"""
        # Title
        title = self.small_font.render("Crafting (2x2)", True, WHITE)
        self.screen.blit(title, (self.crafting_x, self.crafting_y - 20))
        
        # Draw 2x2 or 3x3 grid
        grid_size = 3 if self.crafting_system.is_crafting_table else 2
        
        for row in range(grid_size):
            for col in range(grid_size):
                slot_x = self.crafting_x + col * (self.slot_size + self.margin)
                slot_y = self.crafting_y + row * (self.slot_size + self.margin)
                
                # Draw slot
                pygame.draw.rect(self.screen, GRAY, 
                               (slot_x, slot_y, self.slot_size, self.slot_size))
                pygame.draw.rect(self.screen, BLACK, 
                               (slot_x, slot_y, self.slot_size, self.slot_size), 2)
                
                # Draw item in slot
                item = self.crafting_system.get_item(row, col)
                if item:
                    self.draw_item_icon(slot_x + 2, slot_y + 2, item[0], item[1])
        
        # Draw result slot
        result_x = self.crafting_x + 4 * (self.slot_size + self.margin)
        result_y = self.crafting_y + 1 * (self.slot_size + self.margin)
        
        pygame.draw.rect(self.screen, (150, 150, 150), 
                        (result_x, result_y, self.slot_size, self.slot_size))
        pygame.draw.rect(self.screen, BLACK, 
                        (result_x, result_y, self.slot_size, self.slot_size), 2)
        
        # Draw arrow
        arrow_x = self.crafting_x + 3 * (self.slot_size + self.margin) + 10
        arrow_y = result_y + self.slot_size // 2
        pygame.draw.polygon(self.screen, WHITE, [
            (arrow_x, arrow_y - 5),
            (arrow_x, arrow_y + 5),
            (arrow_x + 15, arrow_y)
        ])
        
        # Draw result
        if self.crafting_system.result:
            result_item, result_count = self.crafting_system.result
            self.draw_item_icon(result_x + 2, result_y + 2, result_item, result_count)
    
    def draw_inventory_grid(self, player):
        """Draw the inventory grid"""
        # Title
        title = self.small_font.render("Inventory", True, WHITE)
        self.screen.blit(title, (self.inventory_x, self.inventory_y - 20))
        
        # Convert inventory to list for grid display
        inventory_items = list(player.inventory.items())
        
        for row in range(self.inventory_rows):
            for col in range(self.inventory_cols):
                slot_x = self.inventory_x + col * (self.slot_size + self.margin)
                slot_y = self.inventory_y + row * (self.slot_size + self.margin)
                
                # Draw slot
                pygame.draw.rect(self.screen, GRAY, 
                               (slot_x, slot_y, self.slot_size, self.slot_size))
                pygame.draw.rect(self.screen, BLACK, 
                               (slot_x, slot_y, self.slot_size, self.slot_size), 2)
                
                # Draw item in slot
                slot_index = row * self.inventory_cols + col
                if slot_index < len(inventory_items):
                    item_type, count = inventory_items[slot_index]
                    self.draw_item_icon(slot_x + 2, slot_y + 2, item_type, count)
    
    def draw_item_icon(self, x, y, item_type, count):
        """Draw an item icon with count"""
        icon_size = self.slot_size - 4
        
        # Draw item color
        color = BLOCK_COLORS.get(item_type, WHITE)
        if color:
            pygame.draw.rect(self.screen, color, (x, y, icon_size, icon_size))
            pygame.draw.rect(self.screen, BLACK, (x, y, icon_size, icon_size), 1)
        
        # Draw count
        if count > 1:
            count_text = self.small_font.render(str(count), True, WHITE)
            text_rect = count_text.get_rect()
            text_rect.bottomright = (x + icon_size - 2, y + icon_size - 2)
            self.screen.blit(count_text, text_rect)