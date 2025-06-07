from .constants import *

# Crafting recipes - format: {result: (count, [(ingredient, count), ...], pattern)}
CRAFTING_RECIPES = {
    # 2x2 recipes (basic crafting)
    BLOCK_WOOD: {
        'count': 4,
        'ingredients': [(BLOCK_WOOD, 1)],
        'pattern': [
            [BLOCK_WOOD, None],
            [None, None]
        ],
        'shapeless': True
    },
    
    # 3x3 recipes (crafting table required)
    'wooden_pickaxe': {
        'count': 1,
        'ingredients': [(BLOCK_WOOD, 3), ('stick', 2)],
        'pattern': [
            [BLOCK_WOOD, BLOCK_WOOD, BLOCK_WOOD],
            [None, 'stick', None],
            [None, 'stick', None]
        ],
        'shapeless': False
    },
    
    'wooden_axe': {
        'count': 1,
        'ingredients': [(BLOCK_WOOD, 3), ('stick', 2)],
        'pattern': [
            [BLOCK_WOOD, BLOCK_WOOD, None],
            [BLOCK_WOOD, 'stick', None],
            [None, 'stick', None]
        ],
        'shapeless': False
    },
    
    'wooden_shovel': {
        'count': 1,
        'ingredients': [(BLOCK_WOOD, 1), ('stick', 2)],
        'pattern': [
            [None, BLOCK_WOOD, None],
            [None, 'stick', None],
            [None, 'stick', None]
        ],
        'shapeless': False
    },
    
    'stick': {
        'count': 4,
        'ingredients': [(BLOCK_WOOD, 2)],
        'pattern': [
            [None, None, None],
            [BLOCK_WOOD, None, None],
            [BLOCK_WOOD, None, None]
        ],
        'shapeless': True
    },
    
    'crafting_table': {
        'count': 1,
        'ingredients': [(BLOCK_WOOD, 4)],
        'pattern': [
            [BLOCK_WOOD, BLOCK_WOOD],
            [BLOCK_WOOD, BLOCK_WOOD]
        ],
        'shapeless': False
    }
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
    
    def get_grid_pattern(self):
        """Get the current crafting grid as a pattern"""
        pattern = []
        grid_size = 3 if self.is_crafting_table else 2
        
        for row in range(grid_size):
            pattern_row = []
            for col in range(grid_size):
                item = self.crafting_grid[row][col]
                if item:
                    pattern_row.append(item[0])
                else:
                    pattern_row.append(None)
            pattern.append(pattern_row)
        
        return pattern
    
    def patterns_match(self, recipe_pattern, grid_pattern):
        """Check if patterns match (with rotation and mirroring for shaped recipes)"""
        def normalize_pattern(pattern):
            """Remove empty rows and columns from pattern"""
            # Remove empty rows
            pattern = [row for row in pattern if any(cell is not None for cell in row)]
            if not pattern:
                return []
            
            # Remove empty columns
            max_cols = len(pattern[0])
            non_empty_cols = []
            for col in range(max_cols):
                if any(row[col] is not None for row in pattern if col < len(row)):
                    non_empty_cols.append(col)
            
            if not non_empty_cols:
                return []
            
            normalized = []
            for row in pattern:
                new_row = [row[col] for col in non_empty_cols if col < len(row)]
                normalized.append(new_row)
            
            return normalized
        
        def rotate_pattern(pattern):
            """Rotate pattern 90 degrees clockwise"""
            if not pattern:
                return []
            rows, cols = len(pattern), len(pattern[0])
            rotated = [[None for _ in range(rows)] for _ in range(cols)]
            for i in range(rows):
                for j in range(cols):
                    rotated[j][rows - 1 - i] = pattern[i][j]
            return rotated
        
        def mirror_pattern(pattern):
            """Mirror pattern horizontally"""
            return [row[::-1] for row in pattern]
        
        # Normalize both patterns
        norm_recipe = normalize_pattern(recipe_pattern)
        norm_grid = normalize_pattern(grid_pattern)
        
        if not norm_recipe or not norm_grid:
            return norm_recipe == norm_grid
        
        # Try all rotations and mirrors
        patterns_to_try = [norm_recipe]
        
        # Add rotations
        current = norm_recipe
        for _ in range(3):
            current = rotate_pattern(current)
            patterns_to_try.append(current)
        
        # Add mirrored versions
        mirrored_patterns = []
        for pattern in patterns_to_try:
            mirrored_patterns.append(mirror_pattern(pattern))
        patterns_to_try.extend(mirrored_patterns)
        
        # Check if any pattern matches
        for pattern in patterns_to_try:
            if len(pattern) == len(norm_grid) and len(pattern[0]) == len(norm_grid[0]):
                match = True
                for i in range(len(pattern)):
                    for j in range(len(pattern[0])):
                        if pattern[i][j] != norm_grid[i][j]:
                            match = False
                            break
                    if not match:
                        break
                if match:
                    return True
        
        return False
    
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
        
        # Get current grid pattern
        grid_pattern = self.get_grid_pattern()
        
        # Check each recipe
        for result_item, recipe_data in CRAFTING_RECIPES.items():
            # Skip 3x3 recipes if not using crafting table
            if not self.is_crafting_table and self.requires_crafting_table(result_item):
                continue
            
            # Check if we have all required ingredients
            can_craft = True
            for req_item, req_count in recipe_data['ingredients']:
                if req_item not in ingredients or ingredients[req_item] < req_count:
                    can_craft = False
                    break
            
            if not can_craft:
                continue
            
            # For shapeless recipes, just check ingredient counts
            if recipe_data.get('shapeless', False):
                total_required = sum(count for _, count in recipe_data['ingredients'])
                total_available = sum(ingredients.values())
                if total_required == total_available:
                    self.result = (result_item, recipe_data['count'])
                    break
            else:
                # For shaped recipes, check pattern
                if self.patterns_match(recipe_data['pattern'], grid_pattern):
                    self.result = (result_item, recipe_data['count'])
                    break
    
    def requires_crafting_table(self, item):
        """Check if an item requires a crafting table to craft"""
        if item not in CRAFTING_RECIPES:
            return False
        
        recipe = CRAFTING_RECIPES[item]
        pattern = recipe['pattern']
        
        # Check if pattern is larger than 2x2
        if len(pattern) > 2 or any(len(row) > 2 for row in pattern):
            return True
        
        return False
    
    def craft_item(self, player_inventory):
        """Attempt to craft the current result"""
        if not self.result:
            return False
        
        result_item, result_count = self.result
        recipe_data = CRAFTING_RECIPES[result_item]
        
        # Check if player has all ingredients in inventory
        for req_item, req_count in recipe_data['ingredients']:
            if req_item not in player_inventory or player_inventory[req_item] < req_count:
                return False
        
        # Remove ingredients from crafting grid
        grid_size = 3 if self.is_crafting_table else 2
        for i in range(grid_size):
            for j in range(grid_size):
                item = self.crafting_grid[i][j]
                if item:
                    item_type, count = item
                    new_count = count - 1
                    if new_count > 0:
                        self.crafting_grid[i][j] = (item_type, new_count)
                    else:
                        self.crafting_grid[i][j] = None
        
        # Add result to player inventory
        if result_item in player_inventory:
            player_inventory[result_item] += result_count
        else:
            player_inventory[result_item] = result_count
        
        # Update result after crafting
        self.update_result()
        return True