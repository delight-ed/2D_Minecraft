from .constants import *

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.smoothing = 0.1
    
    def update(self, player):
        """Update camera to follow player smoothly"""
        # Calculate target position (center camera on player)
        self.target_x = player.x + player.width // 2 - SCREEN_WIDTH // 2
        self.target_y = player.y + player.height // 2 - SCREEN_HEIGHT // 2
        
        # Clamp target to world bounds
        max_x = WORLD_WIDTH * BLOCK_SIZE - SCREEN_WIDTH
        max_y = WORLD_HEIGHT * BLOCK_SIZE - SCREEN_HEIGHT
        
        self.target_x = max(0, min(max_x, self.target_x))
        self.target_y = max(0, min(max_y, self.target_y))
        
        # Smooth camera movement
        self.x += (self.target_x - self.x) * self.smoothing
        self.y += (self.target_y - self.y) * self.smoothing
        
        # Ensure camera stays within bounds
        self.x = max(0, min(max_x, self.x))
        self.y = max(0, min(max_y, self.y))