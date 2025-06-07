from .constants import *

# Crafting recipes - format: {result: (count, [(ingredient, count), ...], pattern)}
CRAFTING_RECIPES = {
    # 2x2 recipes (basic crafting)
    ITEM_STICK: {
        'count': 4,
        'ingredients': [(BLOCK_WOOD, 2)],
        'pattern': [
            [BLOCK_WOOD, None],
            [BLOCK_WOOD, None]
        ],
        'shapeless': False
    },
    
    ITEM_CRAFTING_TABLE: {
        'count': 1,
        'ingredients': [(BLOCK_WOOD, 4)],
        'pattern': [
            [BLOCK_WOOD, BLOCK_WOOD],
            [BLOCK_WOOD, BLOCK_WOOD]
        ],
        'shapeless': False
    },
    
    # Tools (2x2 crafting)
    ITEM_WOODEN_PICKAXE: {
        'count': 1,
        'ingredients': [(BLOCK_WOOD, 3), (ITEM_STICK, 2)],
        'pattern': [
            [BLOCK_WOOD, BLOCK_WOOD],
            [None, ITEM_STICK]
        ],
        'shapeless': False
    },
    
    ITEM_WOODEN_AXE: {
        'count': 1,
        'ingredients': [(BLOCK_WOOD, 3), (ITEM_STICK, 2)],
        'pattern': [
            [BLOCK_WOOD, BLOCK_WOOD],
            [BLOCK_WOOD, ITEM_STICK]
        ],
        'shapeless': False
    },
    
    ITEM_WOODEN_SHOVEL: {
        'count': 1,
        'ingredients': [(BLOCK_WOOD, 1), (ITEM_STICK, 2)],
        'pattern': [
            [BLOCK_WOOD, None],
            [ITEM_STICK, None]
        ],
        'shapeless': False
    },
    
    # Stone tools (requires crafting table - simplified for 2x2)
    ITEM_STONE_PICKAXE: {
        'count': 1,
        'ingredients': [(BLOCK_STONE, 3), (ITEM_STICK, 2)],
        'pattern': [
            [BLOCK_STONE, BLOCK_STONE],
            [None, ITEM_STICK]
        ],
        'shapeless': False
    }
}

class CraftingSystem:
    def __init__(self):
        self.crafting_grid = [[None for _ in range(2)] for _ in range(2)]  # 2x2 grid
        self.result = None
    
    def set_item(self, row, col, item_type, count):
        """Set item in crafting grid"""
        if 0 <= row < 2 and 0 <= col < 2:
            if count > 0:
                self.crafting_grid[row][col] = (item_type, count)
            else:
                self.crafting_grid[row][col] = None
            self.update_result()
    
    def get_item(self, row, col):
        """Get item from crafting grid"""
        if 0 <= row < 2 and 0 <= col < 2:
            return self.crafting_grid[row][col]
        return None
    
    def clear_grid(self):
        """Clear the crafting grid"""
        for i in range(2):
            for j in range(2):
                self.crafting_grid[i][j] = None
        self.update_result()
    
    def get_grid_pattern(self):
        """Get the current crafting grid as a pattern"""
        pattern = []
        
        for row in range(2):
            pattern_row = []
            for col in range(2):
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
            # Remove empty rows from top and bottom
            while pattern and all(cell is None for cell in pattern[0]):
                pattern = pattern[1:]
            while pattern and all(cell is None for cell in pattern[-1]):
                pattern = pattern[:-1]
            
            if not pattern:
                return []
            
            # Remove empty columns from left and right
            max_cols = len(pattern[0])
            
            # Find first non-empty column
            first_col = max_cols
            for col in range(max_cols):
                if any(row[col] is not None for row in pattern if col < len(row)):
                    first_col = col
                    break
            
            # Find last non-empty column
            last_col = -1
            for col in range(max_cols - 1, -1, -1):
                if any(row[col] is not None for row in pattern if col < len(row)):
                    last_col = col
                    break
            
            if first_col > last_col:
                return []
            
            # Extract the non-empty region
            normalized = []
            for row in pattern:
                new_row = row[first_col:last_col + 1]
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
        norm_recipe = normalize_pattern([row[:] for row in recipe_pattern])
        norm_grid = normalize_pattern([row[:] for row in grid_pattern])
        
        if not norm_recipe and not norm_grid:
            return True
        if not norm_recipe or not norm_grid:
            return False
        
        # Try all rotations and mirrors
        patterns_to_try = [norm_recipe]
        
        # Add rotations
        current = [row[:] for row in norm_recipe]
        for _ in range(3):
            current = rotate_pattern(current)
            patterns_to_try.append([row[:] for row in current])
        
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
        
        # Count ingredients in the grid
        ingredients = {}
        for i in range(2):
            for j in range(2):
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
    
    def craft_item(self, player_inventory):
        """Attempt to craft the current result"""
        if not self.result:
            return False
        
        result_item, result_count = self.result
        recipe_data = CRAFTING_RECIPES[result_item]
        
        # Check if we have enough items in the crafting grid
        for req_item, req_count in recipe_data['ingredients']:
            grid_count = 0
            for i in range(2):
                for j in range(2):
                    item = self.crafting_grid[i][j]
                    if item and item[0] == req_item:
                        grid_count += item[1]
            
            if grid_count < req_count:
                return False
        
        # Remove ingredients from crafting grid
        for req_item, req_count in recipe_data['ingredients']:
            remaining_to_remove = req_count
            for i in range(2):
                for j in range(2):
                    if remaining_to_remove <= 0:
                        break
                    item = self.crafting_grid[i][j]
                    if item and item[0] == req_item:
                        remove_count = min(remaining_to_remove, item[1])
                        new_count = item[1] - remove_count
                        remaining_to_remove -= remove_count
                        
                        if new_count > 0:
                            self.crafting_grid[i][j] = (item[0], new_count)
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