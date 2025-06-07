import random
import noise
from .constants import *

class World:
    def __init__(self):
        self.blocks = [[BLOCK_AIR for _ in range(WORLD_HEIGHT)] for _ in range(WORLD_WIDTH)]
        self.generate_world()
    
    def generate_world(self):
        """Generate a simple 2D world with terrain"""
        # Generate height map using Perlin noise
        for x in range(WORLD_WIDTH):
            # Create height variation using noise
            height_noise = noise.pnoise1(x * 0.1, octaves=4, persistence=0.5, lacunarity=2.0)
            surface_height = int(SURFACE_LEVEL + height_noise * 10)
            
            # Clamp surface height
            surface_height = max(10, min(WORLD_HEIGHT - 10, surface_height))
            
            # Fill blocks from bottom to surface
            for y in range(WORLD_HEIGHT):
                if y > surface_height:
                    # Air above surface
                    self.blocks[x][y] = BLOCK_AIR
                elif y == surface_height:
                    # Grass on surface
                    self.blocks[x][y] = BLOCK_GRASS
                elif y > surface_height - 5:
                    # Dirt layer
                    self.blocks[x][y] = BLOCK_DIRT
                else:
                    # Stone below
                    self.blocks[x][y] = BLOCK_STONE
                    
                    # Add some random sand patches near surface
                    if y > surface_height - 8 and random.random() < 0.1:
                        self.blocks[x][y] = BLOCK_SAND
    
    def get_block(self, x, y):
        """Get block at position"""
        if 0 <= x < WORLD_WIDTH and 0 <= y < WORLD_HEIGHT:
            return self.blocks[x][y]
        return BLOCK_AIR
    
    def set_block(self, x, y, block_type):
        """Set block at position"""
        if 0 <= x < WORLD_WIDTH and 0 <= y < WORLD_HEIGHT:
            self.blocks[x][y] = block_type
            return True
        return False
    
    def is_solid(self, x, y):
        """Check if block is solid (not air or water)"""
        block = self.get_block(x, y)
        return block != BLOCK_AIR and block != BLOCK_WATER