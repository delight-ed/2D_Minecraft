from src.constants import *

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.smoothing = 5.0
    
    def update(self, player):
        # Center camera on player
        self.target_x = player.x - SCREEN_WIDTH // 2
        self.target_y = player.y - SCREEN_HEIGHT // 2
        
        # Smooth camera movement
        self.x += (self.target_x - self.x) * self.smoothing * (1/60)  # Assuming 60 FPS
        self.y += (self.target_y - self.y) * self.smoothing * (1/60)
        
        # Keep camera within world bounds
        self.x = max(0, min(self.x, WORLD_WIDTH * BLOCK_SIZE - SCREEN_WIDTH))
        self.y = max(-WORLD_HEIGHT * BLOCK_SIZE + SCREEN_HEIGHT, min(self.y, 0))