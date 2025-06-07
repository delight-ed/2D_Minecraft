from .constants import *

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
    
    def update(self, player):
        """Update camera to follow player"""
        # Center camera on player
        self.x = player.x + player.width // 2 - SCREEN_WIDTH // 2
        self.y = player.y + player.height // 2 - SCREEN_HEIGHT // 2
        
        # Clamp camera to world bounds
        self.x = max(0, min(WORLD_WIDTH * BLOCK_SIZE - SCREEN_WIDTH, self.x))
        self.y = max(0, min(WORLD_HEIGHT * BLOCK_SIZE - SCREEN_HEIGHT, self.y))