import random
import noise
from .constants import *

class World:
    def __init__(self):
        self.blocks = [[BLOCK_AIR for _ in range(WORLD_HEIGHT)] for _ in range(WORLD_WIDTH)]
        self.biomes = [BIOME_PLAINS for _ in range(WORLD_WIDTH)]
        self.generate_world()
    
    def generate_world(self):
        """Generate a realistic 2D world with biomes and structures"""
        # Generate biomes first
        self.generate_biomes()
        
        # Generate terrain
        self.generate_terrain()
        
        # Add ores
        self.generate_ores()
        
        # Add structures
        self.generate_structures()
    
    def generate_biomes(self):
        """Generate biome distribution"""
        for x in range(WORLD_WIDTH):
            biome_noise = noise.pnoise1(x * 0.01, octaves=2, persistence=0.5)
            
            if biome_noise < -0.3:
                self.biomes[x] = BIOME_DESERT
            elif biome_noise < 0.1:
                self.biomes[x] = BIOME_PLAINS
            elif biome_noise < 0.4:
                self.biomes[x] = BIOME_FOREST
            else:
                self.biomes[x] = BIOME_MOUNTAINS
    
    def generate_terrain(self):
        """Generate terrain based on biomes"""
        for x in range(WORLD_WIDTH):
            biome = self.biomes[x]
            
            # Base height with biome variation
            height_noise = noise.pnoise1(x * 0.02, octaves=4, persistence=0.5, lacunarity=2.0)
            
            if biome == BIOME_MOUNTAINS:
                surface_height = int(SURFACE_LEVEL + height_noise * 25)
            elif biome == BIOME_DESERT:
                surface_height = int(SURFACE_LEVEL + height_noise * 8)
            else:
                surface_height = int(SURFACE_LEVEL + height_noise * 12)
            
            # Clamp surface height
            surface_height = max(20, min(WORLD_HEIGHT - 20, surface_height))
            
            # Fill blocks from bottom to surface
            for y in range(WORLD_HEIGHT):
                if y > surface_height:
                    # Air above surface
                    self.blocks[x][y] = BLOCK_AIR
                elif y == surface_height:
                    # Surface block based on biome
                    if biome == BIOME_DESERT:
                        self.blocks[x][y] = BLOCK_SAND
                    else:
                        self.blocks[x][y] = BLOCK_GRASS
                elif y > surface_height - 4:
                    # Dirt layer
                    if biome == BIOME_DESERT:
                        self.blocks[x][y] = BLOCK_SAND
                    else:
                        self.blocks[x][y] = BLOCK_DIRT
                else:
                    # Stone below
                    self.blocks[x][y] = BLOCK_STONE
    
    def generate_ores(self):
        """Generate ore deposits"""
        # Coal ore
        for _ in range(WORLD_WIDTH * 2):
            x = random.randint(0, WORLD_WIDTH - 1)
            y = random.randint(SURFACE_LEVEL - 30, WORLD_HEIGHT - 10)
            
            if self.get_block(x, y) == BLOCK_STONE:
                # Create small coal vein
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if (0 <= x + dx < WORLD_WIDTH and 0 <= y + dy < WORLD_HEIGHT and
                            self.get_block(x + dx, y + dy) == BLOCK_STONE and
                            random.random() < 0.6):
                            self.blocks[x + dx][y + dy] = BLOCK_COAL
        
        # Iron ore (deeper)
        for _ in range(WORLD_WIDTH):
            x = random.randint(0, WORLD_WIDTH - 1)
            y = random.randint(SURFACE_LEVEL - 20, WORLD_HEIGHT - 5)
            
            if self.get_block(x, y) == BLOCK_STONE and random.random() < 0.3:
                self.blocks[x][y] = BLOCK_IRON
    
    def generate_structures(self):
        """Generate trees and other structures"""
        for x in range(5, WORLD_WIDTH - 5):
            biome = self.biomes[x]
            
            # Find surface
            surface_y = None
            for y in range(WORLD_HEIGHT):
                if self.get_block(x, y) != BLOCK_AIR:
                    surface_y = y
                    break
            
            if surface_y is None:
                continue
            
            # Generate trees in forest biome
            if biome == BIOME_FOREST and random.random() < 0.15:
                self.generate_tree(x, surface_y)
            # Occasional trees in plains
            elif biome == BIOME_PLAINS and random.random() < 0.05:
                self.generate_tree(x, surface_y)
    
    def generate_tree(self, x, surface_y):
        """Generate a tree at the given position"""
        tree_height = random.randint(4, 7)
        
        # Tree trunk
        for y in range(surface_y - tree_height, surface_y):
            if 0 <= y < WORLD_HEIGHT:
                self.blocks[x][y] = BLOCK_WOOD
        
        # Tree leaves
        leaf_start = surface_y - tree_height
        for dx in range(-2, 3):
            for dy in range(-2, 1):
                leaf_x = x + dx
                leaf_y = leaf_start + dy
                
                if (0 <= leaf_x < WORLD_WIDTH and 0 <= leaf_y < WORLD_HEIGHT and
                    self.get_block(leaf_x, leaf_y) == BLOCK_AIR and
                    random.random() < 0.8):
                    self.blocks[leaf_x][leaf_y] = BLOCK_LEAVES
    
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