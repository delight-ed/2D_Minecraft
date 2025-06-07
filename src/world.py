import pygame
import random
import math
from src.constants import *

class Block:
    def __init__(self, block_type, hardness=1.0):
        self.type = block_type
        self.hardness = hardness
        self.health = hardness * 10

class Chunk:
    def __init__(self, x):
        self.x = x
        self.blocks = {}
        self.structures = []
        self.biome = BIOME_PLAINS
    
    def get_block(self, x, y):
        return self.blocks.get((x, y), Block(BLOCK_AIR))
    
    def set_block(self, x, y, block):
        if block.type == BLOCK_AIR:
            self.blocks.pop((x, y), None)
        else:
            self.blocks[(x, y)] = block

class World:
    def __init__(self):
        self.chunks = {}
        self.seed = random.randint(0, 1000000)
        self.structures = []
        
    def get_chunk(self, chunk_x):
        if chunk_x not in self.chunks:
            self.chunks[chunk_x] = Chunk(chunk_x)
        return self.chunks[chunk_x]
    
    def get_block(self, x, y):
        if y < 0 or y >= WORLD_HEIGHT:
            return Block(BLOCK_AIR)
        chunk_x = x // CHUNK_SIZE
        local_x = x % CHUNK_SIZE
        chunk = self.get_chunk(chunk_x)
        return chunk.get_block(local_x, y)
    
    def set_block(self, x, y, block):
        if y < 0 or y >= WORLD_HEIGHT:
            return
        chunk_x = x // CHUNK_SIZE
        local_x = x % CHUNK_SIZE
        chunk = self.get_chunk(chunk_x)
        chunk.set_block(local_x, y, block)
    
    def generate_world(self):
        # Generate fewer chunks initially to prevent segfault
        for chunk_x in range(-5, 15):
            self.generate_chunk(chunk_x)
    
    def simple_noise(self, x, frequency=0.01, amplitude=1.0):
        """Simple noise function to replace the problematic noise library"""
        # Use sine waves and random values for terrain generation
        value = 0
        value += math.sin(x * frequency) * amplitude * 0.5
        value += math.sin(x * frequency * 2) * amplitude * 0.25
        value += math.sin(x * frequency * 4) * amplitude * 0.125
        
        # Add some randomness based on seed
        random.seed(int(x + self.seed))
        value += (random.random() - 0.5) * amplitude * 0.3
        
        return value
    
    def generate_chunk(self, chunk_x):
        chunk = self.get_chunk(chunk_x)
        
        # Determine biome using simple math instead of noise
        biome_value = abs(math.sin(chunk_x * 0.1 + self.seed * 0.001)) * 6
        
        if biome_value < 1:
            chunk.biome = BIOME_OCEAN
        elif biome_value < 2:
            chunk.biome = BIOME_DESERT
        elif biome_value < 3:
            chunk.biome = BIOME_PLAINS
        elif biome_value < 4:
            chunk.biome = BIOME_FOREST
        elif biome_value < 5:
            chunk.biome = BIOME_MOUNTAINS
        else:
            chunk.biome = BIOME_SNOW
        
        # Generate terrain
        for local_x in range(CHUNK_SIZE):
            world_x = chunk_x * CHUNK_SIZE + local_x
            self.generate_column(world_x, chunk)
        
        # Generate structures
        self.generate_structures(chunk)
    
    def generate_column(self, x, chunk):
        # Height generation using simple noise
        height = self.simple_noise(x, 0.01, 1.0)
        
        # Add additional octaves
        height += self.simple_noise(x, 0.02, 0.5)
        height += self.simple_noise(x, 0.04, 0.25)
        
        # Adjust height based on biome
        if chunk.biome == BIOME_MOUNTAINS:
            height *= 2
        elif chunk.biome == BIOME_OCEAN:
            height *= 0.3
        elif chunk.biome == BIOME_DESERT:
            height *= 0.7
        
        surface_height = int(WORLD_HEIGHT * 0.6 + height * 30)
        surface_height = max(50, min(surface_height, WORLD_HEIGHT - 50))
        
        local_x = x % CHUNK_SIZE
        
        # Generate bedrock
        for y in range(5):
            chunk.set_block(local_x, y, Block(BLOCK_BEDROCK, 100))
        
        # Generate stone layer
        stone_height = surface_height - random.randint(3, 8)
        for y in range(5, stone_height):
            block_type = BLOCK_STONE
            
            # Add ores
            ore_chance = random.random()
            depth_factor = (stone_height - y) / stone_height
            
            if ore_chance < 0.01 * depth_factor:
                if depth_factor > 0.8:
                    block_type = BLOCK_DIAMOND_ORE
                elif depth_factor > 0.6:
                    block_type = BLOCK_GOLD_ORE
                elif depth_factor > 0.4:
                    block_type = BLOCK_IRON_ORE
                else:
                    block_type = BLOCK_COAL_ORE
            
            chunk.set_block(local_x, y, Block(block_type, 3 if block_type == BLOCK_STONE else 5))
        
        # Generate dirt layer
        dirt_height = surface_height - 1
        for y in range(stone_height, dirt_height):
            chunk.set_block(local_x, y, Block(BLOCK_DIRT, 1))
        
        # Generate surface block based on biome
        surface_block = BLOCK_GRASS
        if chunk.biome == BIOME_DESERT:
            surface_block = BLOCK_SAND
        elif chunk.biome == BIOME_SNOW:
            surface_block = BLOCK_SNOW
        elif chunk.biome == BIOME_OCEAN and surface_height < WORLD_HEIGHT * 0.5:
            surface_block = BLOCK_SAND
        
        chunk.set_block(local_x, surface_height, Block(surface_block, 1))
        
        # Generate water for ocean biome
        if chunk.biome == BIOME_OCEAN:
            water_level = int(WORLD_HEIGHT * 0.55)
            for y in range(surface_height + 1, water_level):
                chunk.set_block(local_x, y, Block(BLOCK_WATER, 0.1))
    
    def generate_structures(self, chunk):
        # Generate trees
        if chunk.biome in [BIOME_FOREST, BIOME_PLAINS]:
            for _ in range(random.randint(1, 3)):
                local_x = random.randint(2, CHUNK_SIZE - 3)
                world_x = chunk.x * CHUNK_SIZE + local_x
                surface_y = self.get_surface_height(world_x)
                
                if surface_y > 0:
                    self.generate_tree(world_x, surface_y + 1)
        
        # Generate cacti in desert
        elif chunk.biome == BIOME_DESERT:
            for _ in range(random.randint(0, 2)):
                local_x = random.randint(1, CHUNK_SIZE - 2)
                world_x = chunk.x * CHUNK_SIZE + local_x
                surface_y = self.get_surface_height(world_x)
                
                if surface_y > 0:
                    self.generate_cactus(world_x, surface_y + 1)
    
    def generate_tree(self, x, y):
        # Tree trunk
        trunk_height = random.randint(4, 7)
        for i in range(trunk_height):
            self.set_block(x, y + i, Block(BLOCK_WOOD, 2))
        
        # Tree leaves
        leaves_y = y + trunk_height
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                if abs(dx) + abs(dy) <= 2 and random.random() > 0.2:
                    self.set_block(x + dx, leaves_y + dy, Block(BLOCK_LEAVES, 0.5))
    
    def generate_cactus(self, x, y):
        height = random.randint(2, 5)
        for i in range(height):
            self.set_block(x, y + i, Block(BLOCK_CACTUS, 1))
    
    def get_surface_height(self, x):
        for y in range(WORLD_HEIGHT - 1, -1, -1):
            block = self.get_block(x, y)
            if block.type != BLOCK_AIR and block.type != BLOCK_WATER:
                return y
        return 0
    
    def break_block(self, x, y, tool_power=1):
        block = self.get_block(x, y)
        if block.type == BLOCK_AIR or block.type == BLOCK_BEDROCK:
            return None
        
        block.health -= tool_power
        if block.health <= 0:
            old_type = block.type
            self.set_block(x, y, Block(BLOCK_AIR))
            return old_type
        return None
    
    def render(self, screen, camera):
        # Calculate visible range
        start_x = max(0, int(camera.x // BLOCK_SIZE) - 2)
        end_x = min(WORLD_WIDTH, int((camera.x + SCREEN_WIDTH) // BLOCK_SIZE) + 2)
        start_y = max(0, int(camera.y // BLOCK_SIZE) - 2)
        end_y = min(WORLD_HEIGHT, int((camera.y + SCREEN_HEIGHT) // BLOCK_SIZE) + 2)
        
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                block = self.get_block(x, y)
                if block.type != BLOCK_AIR:
                    self.render_block(screen, camera, x, y, block)
    
    def render_block(self, screen, camera, x, y, block):
        screen_x = x * BLOCK_SIZE - camera.x
        screen_y = SCREEN_HEIGHT - (y + 1) * BLOCK_SIZE + camera.y
        
        color = self.get_block_color(block.type)
        pygame.draw.rect(screen, color, (screen_x, screen_y, BLOCK_SIZE, BLOCK_SIZE))
        
        # Draw block outline
        pygame.draw.rect(screen, DARK_GRAY, (screen_x, screen_y, BLOCK_SIZE, BLOCK_SIZE), 1)
    
    def get_block_color(self, block_type):
        colors = {
            BLOCK_GRASS: GREEN,
            BLOCK_DIRT: BROWN,
            BLOCK_STONE: GRAY,
            BLOCK_WOOD: (101, 67, 33),
            BLOCK_LEAVES: (34, 139, 34),
            BLOCK_SAND: (238, 203, 173),
            BLOCK_WATER: (0, 191, 255),
            BLOCK_COAL_ORE: (64, 64, 64),
            BLOCK_IRON_ORE: (205, 127, 50),
            BLOCK_GOLD_ORE: (255, 215, 0),
            BLOCK_DIAMOND_ORE: (185, 242, 255),
            BLOCK_BEDROCK: (84, 84, 84),
            BLOCK_SNOW: WHITE,
            BLOCK_ICE: (176, 224, 230),
            BLOCK_CACTUS: (107, 142, 35)
        }
        return colors.get(block_type, WHITE)