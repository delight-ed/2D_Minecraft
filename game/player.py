import pygame
import math
from .constants import *

class Player:
    def __init__(self, x, y, keybinds, texture_manager):
        self.x = x
        self.y = y
        self.width = BLOCK_SIZE - 8
        self.height = BLOCK_SIZE * 2 - 8
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 6
        # Minecraft player can jump exactly 1.25 blocks high
        # With 32px blocks, that's 40 pixels total jump height
        self.jump_power = 12.5  # Adjusted for exactly 1.25 blocks
        self.gravity = 0.8
        self.on_ground = False
        self.keybinds = keybinds
        self.texture_manager = texture_manager
        
        # Empty hotbar - player starts with nothing!
        self.hotbar = [BLOCK_AIR for _ in range(HOTBAR_SIZE)]
        self.selected_slot = 0
        self.inventory = {}
        
        # Tools and mining
        self.current_tool = None
        self.can_mine_stone = False
        
        # Load player textures
        self.load_player_textures()
        
        # No starting items - player must gather everything!
    
    def load_player_textures(self):
        """Load player textures from Minecraft assets"""
        # Try to load Steve skin
        steve_path = "game/assets/minecraft/textures/entity/player/wide/steve.png"
        if os.path.exists(steve_path):
            try:
                self.player_skin = pygame.image.load(steve_path).convert_alpha()
                print("Loaded Steve skin texture")
            except Exception as e:
                print(f"Error loading Steve skin: {e}")
                self.player_skin = None
        else:
            print("Steve skin not found, using fallback")
            self.player_skin = None
    
    def update(self, world):
        """Update player physics and position"""
        # Apply gravity
        self.vel_y += self.gravity
        
        # Limit fall speed
        if self.vel_y > 20:
            self.vel_y = 20
        
        # Move horizontally with better collision
        new_x = self.x + self.vel_x
        if not self.check_collision_horizontal(world, new_x, self.y):
            self.x = new_x
        
        # Move vertically with better collision
        new_y = self.y + self.vel_y
        if self.check_collision_vertical(world, self.x, new_y):
            if self.vel_y > 0:  # Falling
                self.on_ground = True
            self.vel_y = 0
        else:
            self.y = new_y
            self.on_ground = False
        
        # Update tool status
        self.update_tool_status()
    
    def check_collision_horizontal(self, world, x, y):
        """Check horizontal collision with better precision"""
        # Check multiple points along the player's height
        check_points = [
            (x + 2, y + 2),                    # Top-left
            (x + self.width - 2, y + 2),       # Top-right
            (x + 2, y + self.height // 2),     # Middle-left
            (x + self.width - 2, y + self.height // 2),  # Middle-right
            (x + 2, y + self.height - 2),      # Bottom-left
            (x + self.width - 2, y + self.height - 2)    # Bottom-right
        ]
        
        for point_x, point_y in check_points:
            block_x = int(point_x // BLOCK_SIZE)
            block_y = int(point_y // BLOCK_SIZE)
            if world.is_solid(block_x, block_y):
                return True
        return False
    
    def check_collision_vertical(self, world, x, y):
        """Check vertical collision with better precision"""
        # Check multiple points along the player's width
        check_points = [
            (x + 2, y + 2),                    # Top-left
            (x + self.width // 2, y + 2),      # Top-center
            (x + self.width - 2, y + 2),       # Top-right
            (x + 2, y + self.height - 2),      # Bottom-left
            (x + self.width // 2, y + self.height - 2),  # Bottom-center
            (x + self.width - 2, y + self.height - 2)    # Bottom-right
        ]
        
        for point_x, point_y in check_points:
            block_x = int(point_x // BLOCK_SIZE)
            block_y = int(point_y // BLOCK_SIZE)
            if world.is_solid(block_x, block_y):
                return True
        return False
    
    def handle_input(self, keys):
        """Handle player input using configurable keybinds"""
        self.vel_x = 0
        
        # Convert keybind strings to pygame keys
        def get_key_pressed(keybind_name):
            key_name = self.keybinds.get(keybind_name, '')
            if key_name == 'space':
                return keys[pygame.K_SPACE]
            elif len(key_name) == 1:
                return keys[getattr(pygame, f'K_{key_name}', pygame.K_UNKNOWN)]
            return False
        
        if get_key_pressed('move_left'):
            self.vel_x = -self.speed
        if get_key_pressed('move_right'):
            self.vel_x = self.speed
        if get_key_pressed('jump') and self.on_ground:
            self.vel_y = -self.jump_power
    
    def select_hotbar_slot(self, slot):
        """Select hotbar slot"""
        if 0 <= slot < HOTBAR_SIZE:
            self.selected_slot = slot
    
    def get_selected_block(self):
        """Get currently selected block type"""
        if self.selected_slot < len(self.hotbar):
            return self.hotbar[self.selected_slot]
        return BLOCK_AIR
    
    def update_tool_status(self):
        """Update what the player can mine based on tools"""
        selected_block = self.get_selected_block()
        
        # Check if player has a pickaxe to mine stone
        self.can_mine_stone = False
        for item_type in self.inventory:
            if isinstance(item_type, str) and 'pickaxe' in item_type:
                self.can_mine_stone = True
                break
    
    def has_line_of_sight(self, world, target_x, target_y):
        """Check if player has clear line of sight to target position"""
        # Check from all four corners of player's head (top portion)
        head_height = self.height // 3  # Top third of player
        check_points = [
            (self.x + 2, self.y + 2),                           # Top-left corner
            (self.x + self.width - 2, self.y + 2),              # Top-right corner
            (self.x + 2, self.y + head_height),                 # Mid-left of head
            (self.x + self.width - 2, self.y + head_height)     # Mid-right of head
        ]
        
        # If any corner has line of sight, allow the action
        for start_x, start_y in check_points:
            if self.check_line_of_sight_from_point(world, start_x, start_y, target_x, target_y):
                return True
        
        return False
    
    def check_line_of_sight_from_point(self, world, start_x, start_y, target_x, target_y):
        """Check line of sight from a specific point to target"""
        # Use Bresenham's line algorithm to check each block along the path
        dx = abs(target_x - start_x)
        dy = abs(target_y - start_y)
        
        x = int(start_x // BLOCK_SIZE)
        y = int(start_y // BLOCK_SIZE)
        
        x_inc = 1 if target_x > start_x else -1
        y_inc = 1 if target_y > start_y else -1
        
        error = dx - dy
        
        target_block_x = int(target_x // BLOCK_SIZE)
        target_block_y = int(target_y // BLOCK_SIZE)
        
        while x != target_block_x or y != target_block_y:
            # Don't check the target block itself
            if world.is_solid(x, y):
                return False
            
            if error > 0:
                x += x_inc
                error -= dy
            else:
                y += y_inc
                error += dx
        
        return True
    
    def can_mine_block(self, block_type):
        """Check if player can mine this block type"""
        if block_type == BLOCK_AIR:
            return False
        
        # Leaves can only be mined with shears (for now, anyone can mine them but they don't drop)
        if block_type == BLOCK_LEAVES:
            return True
        
        # Stone requires a pickaxe
        if block_type in [BLOCK_STONE, BLOCK_COAL, BLOCK_IRON]:
            return self.can_mine_stone
        
        # Other blocks can be mined by hand
        return True
    
    def get_block_drops(self, block_type):
        """Get what items drop when mining a block"""
        # Leaves don't drop anything unless mined with shears
        if block_type == BLOCK_LEAVES:
            return []
        
        # Most blocks drop themselves
        return [block_type]
    
    def add_to_inventory(self, block_type):
        """Add block to inventory and try to put it in hotbar"""
        if block_type in self.inventory:
            self.inventory[block_type] += 1
        else:
            self.inventory[block_type] = 1
        
        # Try to add to hotbar if there's an empty slot
        if block_type not in self.hotbar:
            for i in range(len(self.hotbar)):
                if self.hotbar[i] == BLOCK_AIR:
                    self.hotbar[i] = block_type
                    break
    
    def mine_block(self, world, mouse_x, mouse_y, camera_x, camera_y):
        """Mine block at mouse position with improved line of sight check"""
        world_x = int((mouse_x + camera_x) // BLOCK_SIZE)
        world_y = int((mouse_y + camera_y) // BLOCK_SIZE)
        
        # Check mining range
        player_center_x = self.x + self.width // 2
        player_center_y = self.y + self.height // 2
        block_center_x = world_x * BLOCK_SIZE + BLOCK_SIZE // 2
        block_center_y = world_y * BLOCK_SIZE + BLOCK_SIZE // 2
        
        distance = ((player_center_x - block_center_x) ** 2 + (player_center_y - block_center_y) ** 2) ** 0.5
        
        if distance > BLOCK_SIZE * 5:  # Mining range limit
            return False
        
        # Check line of sight from player's head
        if not self.has_line_of_sight(world, block_center_x, block_center_y):
            return False
        
        block_type = world.get_block(world_x, world_y)
        
        if block_type != BLOCK_AIR and self.can_mine_block(block_type):
            world.set_block(world_x, world_y, BLOCK_AIR)
            
            # Create item drops
            drops = self.get_block_drops(block_type)
            for drop in drops:
                world.add_item_drop(block_center_x, block_center_y, drop)
            
            return True
        return False
    
    def place_block(self, world, mouse_x, mouse_y, camera_x, camera_y):
        """Place block at mouse position with improved placement rules"""
        world_x = int((mouse_x + camera_x) // BLOCK_SIZE)
        world_y = int((mouse_y + camera_y) // BLOCK_SIZE)
        
        # Check placement range
        player_center_x = self.x + self.width // 2
        player_center_y = self.y + self.height // 2
        block_center_x = world_x * BLOCK_SIZE + BLOCK_SIZE // 2
        block_center_y = world_y * BLOCK_SIZE + BLOCK_SIZE // 2
        
        distance = ((player_center_x - block_center_x) ** 2 + (player_center_y - block_center_y) ** 2) ** 0.5
        
        if distance > BLOCK_SIZE * 5:  # Placement range limit
            return False
        
        # Check line of sight from player's head
        if not self.has_line_of_sight(world, block_center_x, block_center_y):
            return False
        
        # Check if target position is air
        if world.get_block(world_x, world_y) != BLOCK_AIR:
            return False
        
        # Check if there's a solid block adjacent (can't place in mid-air)
        adjacent_positions = [
            (world_x - 1, world_y),  # Left
            (world_x + 1, world_y),  # Right
            (world_x, world_y - 1),  # Above
            (world_x, world_y + 1)   # Below
        ]
        
        has_adjacent_solid = False
        for adj_x, adj_y in adjacent_positions:
            if world.is_solid(adj_x, adj_y):
                has_adjacent_solid = True
                break
        
        if not has_adjacent_solid:
            return False  # Can't place in mid-air
        
        block_type = self.get_selected_block()
        
        if block_type != BLOCK_AIR:
            if block_type in self.inventory and self.inventory[block_type] > 0:
                # Don't place block inside player
                test_rect = pygame.Rect(world_x * BLOCK_SIZE, world_y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
                
                if not test_rect.colliderect(player_rect):
                    world.set_block(world_x, world_y, block_type)
                    self.inventory[block_type] -= 1
                    if self.inventory[block_type] == 0:
                        del self.inventory[block_type]
                        # Remove from hotbar if count reaches 0
                        for i in range(len(self.hotbar)):
                            if self.hotbar[i] == block_type:
                                self.hotbar[i] = BLOCK_AIR
                                break
                    return True
        return False
    
    def pickup_items(self, world):
        """Pick up nearby item drops"""
        player_rect = pygame.Rect(self.x - BLOCK_SIZE, self.y - BLOCK_SIZE, 
                                 self.width + BLOCK_SIZE * 2, self.height + BLOCK_SIZE * 2)
        
        for item in world.item_drops[:]:  # Copy list to avoid modification during iteration
            item_rect = pygame.Rect(item['x'] - 8, item['y'] - 8, 16, 16)
            if player_rect.colliderect(item_rect):
                self.add_to_inventory(item['type'])
                world.item_drops.remove(item)
    
    def draw(self, screen, camera_x, camera_y):
        """Draw player with Minecraft Steve texture or fallback"""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Only draw if player is on screen
        if (-self.width <= screen_x <= SCREEN_WIDTH and -self.height <= screen_y <= SCREEN_HEIGHT):
            if self.player_skin:
                # Extract parts from Steve skin texture for 2D representation
                self.draw_steve_2d(screen, screen_x, screen_y)
            else:
                # Fallback to original 8-bit style
                self.draw_fallback_player(screen, screen_x, screen_y)
    
    def draw_steve_2d(self, screen, screen_x, screen_y):
        """Draw 2D representation of Steve using Minecraft skin texture"""
        try:
            # Steve skin is 64x64, we need to extract the front face parts
            # Head: (8, 8, 8, 8) - front face of head
            # Body: (20, 20, 8, 12) - front of body
            # Arms: (44, 20, 4, 12) - front of right arm
            # Legs: (4, 20, 4, 12) - front of right leg
            
            # Scale factor to fit our player size
            scale_x = self.width / 8  # 8 pixels wide in texture
            scale_y = self.height / 20  # Approximate total height
            
            # Head (top quarter of player)
            head_height = self.height // 4
            head_rect = pygame.Rect(screen_x, screen_y, self.width, head_height)
            
            # Extract and scale head texture
            head_texture = self.player_skin.subsurface((8, 8, 8, 8))
            head_scaled = pygame.transform.scale(head_texture, (self.width, head_height))
            screen.blit(head_scaled, head_rect)
            
            # Body (middle portion)
            body_height = self.height // 2
            body_rect = pygame.Rect(screen_x, screen_y + head_height, self.width, body_height)
            
            # Extract and scale body texture
            body_texture = self.player_skin.subsurface((20, 20, 8, 12))
            body_scaled = pygame.transform.scale(body_texture, (self.width, body_height))
            screen.blit(body_scaled, body_rect)
            
            # Legs (bottom quarter)
            legs_height = self.height // 4
            legs_rect = pygame.Rect(screen_x, screen_y + head_height + body_height, self.width, legs_height)
            
            # Extract and scale leg texture
            leg_texture = self.player_skin.subsurface((4, 20, 4, 12))
            leg_scaled = pygame.transform.scale(leg_texture, (self.width, legs_height))
            screen.blit(leg_scaled, legs_rect)
            
            # Draw simple arms on the sides
            arm_width = 3
            arm_height = body_height // 2
            arm_texture = self.player_skin.subsurface((44, 20, 4, 12))
            
            # Left arm
            left_arm_scaled = pygame.transform.scale(arm_texture, (arm_width, arm_height))
            screen.blit(left_arm_scaled, (screen_x - arm_width, screen_y + head_height))
            
            # Right arm
            right_arm_scaled = pygame.transform.scale(arm_texture, (arm_width, arm_height))
            screen.blit(right_arm_scaled, (screen_x + self.width, screen_y + head_height))
            
        except Exception as e:
            print(f"Error drawing Steve texture: {e}")
            # Fall back to simple rendering
            self.draw_fallback_player(screen, screen_x, screen_y)
    
    def draw_fallback_player(self, screen, screen_x, screen_y):
        """Draw player with 8-bit style (fallback)"""
        # Draw player body with 8-bit style
        body_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        
        # Main body color (blue shirt)
        pygame.draw.rect(screen, (0, 100, 200), body_rect)
        
        # Head (top quarter)
        head_height = self.height // 4
        head_rect = pygame.Rect(screen_x, screen_y, self.width, head_height)
        pygame.draw.rect(screen, (255, 220, 177), head_rect)  # Skin color
        
        # Pants (bottom half)
        pants_height = self.height // 2
        pants_rect = pygame.Rect(screen_x, screen_y + self.height - pants_height, self.width, pants_height)
        pygame.draw.rect(screen, (50, 50, 150), pants_rect)  # Dark blue pants
        
        # Body outline
        pygame.draw.rect(screen, BLACK, body_rect, 2)
        
        # Draw pixelated face
        eye_size = 2
        # Eyes
        pygame.draw.rect(screen, BLACK, (int(screen_x + self.width * 0.25), int(screen_y + 6), eye_size, eye_size))
        pygame.draw.rect(screen, BLACK, (int(screen_x + self.width * 0.75 - eye_size), int(screen_y + 6), eye_size, eye_size))
        
        # Mouth (simple line)
        mouth_y = int(screen_y + 12)
        pygame.draw.rect(screen, BLACK, (int(screen_x + self.width * 0.4), mouth_y, int(self.width * 0.2), 1))
        
        # Arms (simple rectangles on sides)
        arm_width = 4
        arm_height = self.height // 3
        # Left arm
        pygame.draw.rect(screen, (255, 220, 177), (screen_x - arm_width, screen_y + head_height, arm_width, arm_height))
        pygame.draw.rect(screen, BLACK, (screen_x - arm_width, screen_y + head_height, arm_width, arm_height), 1)
        # Right arm
        pygame.draw.rect(screen, (255, 220, 177), (screen_x + self.width, screen_y + head_height, arm_width, arm_height))
        pygame.draw.rect(screen, BLACK, (screen_x + self.width, screen_y + head_height, arm_width, arm_height), 1)