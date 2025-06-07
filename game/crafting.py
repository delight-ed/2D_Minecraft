from .constants import *

# Crafting recipes - format: {result: (count, [(ingredient, count), ...])}
CRAFTING_RECIPES = {
    # 2x2 recipes (basic crafting)
    BLOCK_WOOD: (4, [(BLOCK_WOOD, 1)]),  # Wood planks from logs
    
    # 3x3 recipes (crafting table required)
    'wooden_pickaxe': (1, [(BLOCK_WOOD, 3), ('stick', 2)]),
    'wooden_axe': (1, [(BLOCK_WOOD, 3), ('stick', 2)]),
    'wooden_shovel': (1, [(BLOCK_WOOD, 1), ('stick', 2)]),
    'stick': (4, [(BLOCK_WOOD, 2)]),
    'crafting_table': (1, [(BLOCK_WOOD, 4)]),
}

class CraftingSystem:
    def __init__(self):
        self.crafting_grid = [[None for _ in range(3)] for _ in range(3)]
        self.result = None
        self.is_crafting_table = False
    
    def set_crafting_table_mode(self, enabled):
        """Enable or disable crafting table mode (3x3 vs 2x2)"""
        self.is_crafting_table = enabled
        if not enabled:
            # Clear the 3x3 grid when switching to 2x2
            for i in range(3):
                for j in range(3):
                    if i >= 2 or j >= 2:
                        self.crafting_grid[i][j] = None
        self.update_result()
    
    def set_item(self, row, col, item_type, count):
        """Set item in crafting grid"""
        max_size = 3 if self.is_crafting_table else 2
        if 0 <= row < max_size and 0 <= col < max_size:
            if count > 0:
                self.crafting_grid[row][col] = (item_type, count)
            else:
                self.crafting_grid[row][col] = None
            self.update_result()
    
    def get_item(self, row, col):
        """Get item from crafting grid"""
        if 0 <= row < 3 and 0 <= col < 3:
            return self.crafting_grid[row][col]
        return None
    
    def clear_grid(self):
        """Clear the crafting grid"""
        for i in range(3):
            for j in range(3):
                self.crafting_grid[i][j] = None
        self.update_result()
    
    def update_result(self):
        """Update the crafting result based on current grid"""
        self.result = None
        
        # Get the effective grid size
        grid_size = 3 if self.is_crafting_table else 2
        
        # Count ingredients in the grid
        ingredients = {}
        for i in range(grid_size):
            for j in range(grid_size):
                item = self.crafting_grid[i][j]
                if item:
                    item_type, count = item
                    if item_type in ingredients:
                        ingredients[item_type] += count
                    else:
                        ingredients[item_type] = count
        
        # Check each recipe
        for result_item, (result_count, recipe_ingredients) in CRAFTING_RECIPES.items():
            # Skip 3x3 recipes if not using crafting table
            if not self.is_crafting_table and self.requires_crafting_table(result_item):
                continue
            
            # Check if we have all required ingredients
            can_craft = True
            for req_item, req_count in recipe_ingredients:
                if req_item not in ingredients or ingredients[req_item] < req_count:
                    can_craft = False
                    break
            
            # Check if we have exactly the required ingredients (no extras)
            if can_craft:
                total_required = sum(count for _, count in recipe_ingredients)
                total_available = sum(ingredients.values())
                if total_required == total_available:
                    self.result = (result_item, result_count)
                    break
    
    def requires_crafting_table(self, item):
        """Check if an item requires a crafting table to craft"""
        crafting_table_items = ['wooden_pickaxe', 'wooden_axe', 'wooden_shovel', 'stick']
        return item in crafting_table_items
    
    def craft_item(self, player_inventory):
        """Attempt to craft the current result"""
        if not self.result:
            return False
        
        result_item, result_count = self.result
        recipe_ingredients = CRAFTING_RECIPES[result_item][1]
        
        # Check if player has all ingredients
        for req_item, req_count in recipe_ingredients:
            if req_item not in player_inventory or player_inventory[req_item] < req_count:
                return False
        
        # Remove ingredients from player inventory
        for req_item, req_count in recipe_ingredients:
            player_inventory[req_item] -= req_count
            if player_inventory[req_item] == 0:
                del player_inventory[req_item]
        
        # Add result to player inventory
        if result_item in player_inventory:
            player_inventory[result_item] += result_count
        else:
            player_inventory[result_item] = result_count
        
        # Clear the crafting grid
        self.clear_grid()
        return True