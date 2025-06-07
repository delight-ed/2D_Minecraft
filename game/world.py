import random
import noise
import json
import os
from .constants import *

class Chunk:
    def __init__(self, chunk_x):
        self.chunk_x = chunk_x
        self.blocks = [[BLOCK_AIR for _ in range(WORLD_HEIGHT)] for _ in range(CHUNK_SIZE)]
        self.biomes = [BIOME_PLAINS for _ in range(CHUNK_SIZE)]
        self.generated = False
        self.modified = False  # Track if chunk has been modified
    
    def generate(self, world_seed=0):
        """Generate this chunk"""
        if self.generated:
            return
        
        # Set random seed for consistent generation
        random.seed(world_seed + self.chunk_x * 1000)
        
        # Generate biomes for this chunk
        for local_x in range(CHUNK_SIZE):
            world_x = self.chunk_x * CHUNK_SIZE + local_x
            biome_noise = noise.pnoise1(world_x * 0.01, octaves=2, persistence=0.5)
            
            if biome_noise < -0.3:
                self.biomes[local_x] = BIOME_DESERT
            elif biome_noise < 0.1:
                self.biomes[local_x] = BIOME_PLAINS
            elif biome_noise < 0.4:
                self.biomes[local_x] = BIOME_FOREST
            else:
                self.biomes[local_x] = BIOME_MOUNTAINS
        
        # Generate terrain
        for local_x in range(CHUNK_SIZE):
            world_x = self.chunk_x * CHUNK_SIZE + local_x
            biome = self.biomes[local_x]
            
            # Base height with biome variation
            height_noise = noise.pnoise1(world_x * 0.02, octaves=4, persistence=0.5, lacunarity=2.0)
            
            if biome == BIOME_MOUNTAINS:
                surface_height = int(SURFACE_LEVEL + height_noise * 25)
            elif biome == BIOME_DESERT:
                surface_height = int(SURFACE_LEVEL + height_noise * 8)
            else:
                surface_height = int(SURFACE_LEVEL + height_noise * 12)
            
            # Clamp surface height
            surface_height = max(20, min(WORLD_HEIGHT - 20, surface_height))
            
            # Fill blocks from surface down to bottom
            for y in range(WORLD_HEIGHT):
                if y < surface_height:
                    # Air above surface
                    self.blocks[local_x][y] = BLOCK_AIR
                elif y == surface_height:
                    # Surface block based on biome
                    if biome == BIOME_DESERT:
                        self.blocks[local_x][y] = BLOCK_SAND
                    else:
                        self.blocks[local_x][y] = BLOCK_GRASS
                elif y < surface_height + 4:
                    # Dirt layer below surface
                    if biome == BIOME_DESERT:
                        self.blocks[local_x][y] = BLOCK_SAND
                    else:
                        self.blocks[local_x][y] = BLOCK_DIRT
                else:
                    # Stone below dirt
                    self.blocks[local_x][y] = BLOCK_STONE
        
        # Generate ores
        self.generate_ores()
        
        # Generate structures
        self.generate_structures()
        
        self.generated = True
        
        # Reset random seed
        random.seed()
    
    def generate_ores(self):
        """Generate ore deposits in this chunk"""
        # Coal ore (closer to surface)
        for _ in range(CHUNK_SIZE // 4):
            local_x = random.randint(0, CHUNK_SIZE - 1)
            y = random.randint(SURFACE_LEVEL + 10, WORLD_HEIGHT - 10)
            
            if self.get_block(local_x, y) == BLOCK_STONE:
                # Create small coal vein
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if (0 <= local_x + dx < CHUNK_SIZE and 0 <= y + dy < WORLD_HEIGHT and
                            self.get_block(local_x + dx, y + dy) == BLOCK_STONE and
                            random.random() < 0.6):
                            self.blocks[local_x + dx][y + dy] = BLOCK_COAL
        
        # Iron ore (deeper)
        for _ in range(CHUNK_SIZE // 8):
            local_x = random.randint(0, CHUNK_SIZE - 1)
            y = random.randint(SURFACE_LEVEL + 20, WORLD_HEIGHT - 5)
            
            if self.get_block(local_x, y) == BLOCK_STONE and random.random() < 0.3:
                self.blocks[local_x][y] = BLOCK_IRON
    
    def generate_structures(self):
        """Generate trees and other structures in this chunk"""
        for local_x in range(2, CHUNK_SIZE - 2):
            biome = self.biomes[local_x]
            
            # Find surface
            surface_y = None
            for y in range(WORLD_HEIGHT):
                if self.get_block(local_x, y) != BLOCK_AIR:
                    surface_y = y
                    break
            
            if surface_y is None:
                continue
            
            # Generate trees in forest biome
            if biome == BIOME_FOREST and random.random() < 0.15:
                self.generate_tree(local_x, surface_y)
            # Occasional trees in plains
            elif biome == BIOME_PLAINS and random.random() < 0.05:
                self.generate_tree(local_x, surface_y)
    
    def generate_tree(self, local_x, surface_y):
        """Generate a tree at the given position"""
        tree_height = random.randint(4, 7)
        
        # Tree trunk (going up from surface)
        for i in range(tree_height):
            trunk_y = surface_y - 1 - i
            if trunk_y >= 0:
                self.blocks[local_x][trunk_y] = BLOCK_WOOD
        
        # Tree leaves (crown above trunk)
        leaf_center_y = surface_y - tree_height - 1
        for dx in range(-2, 3):
            for dy in range(-2, 1):
                leaf_x = local_x + dx
                leaf_y = leaf_center_y + dy
                
                if (0 <= leaf_x < CHUNK_SIZE and 0 <= leaf_y >= 0 and
                    self.get_block(leaf_x, leaf_y) == BLOCK_AIR and
                    random.random() < 0.8):
                    self.blocks[leaf_x][leaf_y] = BLOCK_LEAVES
    
    def get_block(self, local_x, y):
        """Get block at local position within chunk"""
        if 0 <= local_x < CHUNK_SIZE and 0 <= y < WORLD_HEIGHT:
            return self.blocks[local_x][y]
        return BLOCK_AIR
    
    def set_block(self, local_x, y, block_type):
        """Set block at local position within chunk"""
        if 0 <= local_x < CHUNK_SIZE and 0 <= y < WORLD_HEIGHT:
            self.blocks[local_x][y] = block_type
            self.modified = True  # Mark chunk as modified
            return True
        return False
    
    def to_dict(self):
        """Convert chunk to dictionary for saving"""
        return {
            'chunk_x': self.chunk_x,
            'blocks': self.blocks,
            'biomes': self.biomes,
            'generated': self.generated,
            'modified': self.modified
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create chunk from dictionary"""
        chunk = cls(data['chunk_x'])
        chunk.blocks = data['blocks']
        chunk.biomes = data['biomes']
        chunk.generated = data['generated']
        chunk.modified = data.get('modified', False)
        return chunk


class World:
    def __init__(self, seed=None, save_name="default"):
        self.seed = seed or random.randint(0, 1000000)
        self.save_name = save_name
        self.save_dir = f"saves/{save_name}"
        
        # Create save directory if it doesn't exist
        os.makedirs(self.save_dir, exist_ok=True)
        
        random.seed(self.seed)
        self.chunks = {}  # Dictionary of chunk_x -> Chunk
        self.item_drops = []  # List of item drops in the world
        
        # Try to load existing world data
        self.load_world_data()
        
        # Generate initial chunks around spawn if this is a new world
        if not self.chunks:
            spawn_chunk = 0
            for chunk_x in range(spawn_chunk - 2, spawn_chunk + 3):
                self.load_chunk(chunk_x)
    
    def save_world_data(self):
        """Save world metadata"""
        world_data = {
            'seed': self.seed,
            'save_name': self.save_name
        }
        
        with open(f"{self.save_dir}/world.json", 'w') as f:
            json.dump(world_data, f)
    
    def load_world_data(self):
        """Load world metadata"""
        world_file = f"{self.save_dir}/world.json"
        if os.path.exists(world_file):
            try:
                with open(world_file, 'r') as f:
                    world_data = json.load(f)
                    self.seed = world_data.get('seed', self.seed)
                    print(f"Loaded world with seed: {self.seed}")
            except Exception as e:
                print(f"Error loading world data: {e}")
    
    def save_chunk(self, chunk):
        """Save a single chunk to disk"""
        if chunk.modified:
            chunk_file = f"{self.save_dir}/chunk_{chunk.chunk_x}.json"
            try:
                with open(chunk_file, 'w') as f:
                    json.dump(chunk.to_dict(), f)
                chunk.modified = False  # Reset modified flag after saving
            except Exception as e:
                print(f"Error saving chunk {chunk.chunk_x}: {e}")
    
    def load_chunk_from_disk(self, chunk_x):
        """Load a chunk from disk"""
        chunk_file = f"{self.save_dir}/chunk_{chunk_x}.json"
        if os.path.exists(chunk_file):
            try:
                with open(chunk_file, 'r') as f:
                    chunk_data = json.load(f)
                    return Chunk.from_dict(chunk_data)
            except Exception as e:
                print(f"Error loading chunk {chunk_x}: {e}")
        return None
    
    def load_chunk(self, chunk_x):
        """Load a chunk if it doesn't exist"""
        if chunk_x not in self.chunks:
            # Try to load from disk first
            chunk = self.load_chunk_from_disk(chunk_x)
            
            if chunk is None:
                # Generate new chunk if not found on disk
                chunk = Chunk(chunk_x)
                chunk.generate(self.seed)
            
            self.chunks[chunk_x] = chunk
    
    def unload_distant_chunks(self, player_chunk_x):
        """Unload chunks that are too far from the player"""
        chunks_to_unload = []
        for chunk_x in self.chunks:
            if abs(chunk_x - player_chunk_x) > RENDER_DISTANCE + 2:
                chunks_to_unload.append(chunk_x)
        
        for chunk_x in chunks_to_unload:
            # Save chunk before unloading if it was modified
            self.save_chunk(self.chunks[chunk_x])
            del self.chunks[chunk_x]
    
    def ensure_chunks_loaded(self, player_x):
        """Ensure chunks around player are loaded"""
        player_chunk_x = int(player_x // (CHUNK_SIZE * BLOCK_SIZE))
        
        # Load chunks in render distance
        for chunk_x in range(player_chunk_x - RENDER_DISTANCE, player_chunk_x + RENDER_DISTANCE + 1):
            self.load_chunk(chunk_x)
        
        # Unload distant chunks to save memory
        self.unload_distant_chunks(player_chunk_x)
    
    def world_to_chunk_coords(self, world_x):
        """Convert world x coordinate to chunk coordinates"""
        chunk_x = world_x // CHUNK_SIZE
        local_x = world_x % CHUNK_SIZE
        if world_x < 0 and local_x != 0:
            chunk_x -= 1
            local_x = CHUNK_SIZE + local_x
        return chunk_x, local_x
    
    def get_block(self, x, y):
        """Get block at world position"""
        if y < 0 or y >= WORLD_HEIGHT:
            return BLOCK_AIR
        
        chunk_x, local_x = self.world_to_chunk_coords(x)
        
        if chunk_x in self.chunks:
            return self.chunks[chunk_x].get_block(local_x, y)
        return BLOCK_AIR
    
    def set_block(self, x, y, block_type):
        """Set block at world position"""
        if y < 0 or y >= WORLD_HEIGHT:
            return False
        
        chunk_x, local_x = self.world_to_chunk_coords(x)
        
        # Load chunk if needed
        self.load_chunk(chunk_x)
        
        if chunk_x in self.chunks:
            return self.chunks[chunk_x].set_block(local_x, y, block_type)
        return False
    
    def is_solid(self, x, y):
        """Check if block is solid (not air or water)"""
        block = self.get_block(x, y)
        return block != BLOCK_AIR and block != BLOCK_WATER
    
    def add_item_drop(self, x, y, item_type):
        """Add an item drop to the world"""
        self.item_drops.append({
            'x': x,
            'y': y,
            'type': item_type,
            'vel_y': -2,  # Initial upward velocity
            'vel_x': random.uniform(-1, 1),  # Random horizontal velocity
            'time': 0,
            'on_ground': False,
            'count': 1  # Stack count
        })
    
    def update_item_drops(self):
        """Update physics for item drops with stacking"""
        for item in self.item_drops:
            item['time'] += 1
            
            # Apply gravity only if not on ground
            if not item['on_ground']:
                item['vel_y'] += 0.5
                if item['vel_y'] > 10:
                    item['vel_y'] = 10
            
            # Stop horizontal movement when on ground (no sliding)
            if item['on_ground']:
                item['vel_x'] = 0
            else:
                # Apply air resistance to horizontal movement
                item['vel_x'] *= 0.95
            
            # Move item
            new_x = item['x'] + item['vel_x']
            new_y = item['y'] + item['vel_y']
            
            # Check horizontal collision
            block_x = int(new_x // BLOCK_SIZE)
            block_y = int(item['y'] // BLOCK_SIZE)
            
            if not self.is_solid(block_x, block_y):
                item['x'] = new_x
            else:
                item['vel_x'] = 0
            
            # Check vertical collision
            block_x = int(item['x'] // BLOCK_SIZE)
            block_y = int((new_y + 8) // BLOCK_SIZE)  # Check bottom of item
            
            if self.is_solid(block_x, block_y) and item['vel_y'] > 0:
                # Find the exact top of the block
                item['y'] = block_y * BLOCK_SIZE - 8
                item['vel_y'] = 0
                item['on_ground'] = True
            else:
                item['y'] = new_y
                # Check if item should start falling (block below was removed)
                if item['on_ground']:
                    # Check if there's still a solid block below
                    below_block_x = int(item['x'] // BLOCK_SIZE)
                    below_block_y = int((item['y'] + 9) // BLOCK_SIZE)
                    if not self.is_solid(below_block_x, below_block_y):
                        item['on_ground'] = False
                        item['vel_y'] = 0  # Start falling from rest
        
        # Stack nearby items of the same type
        self.stack_nearby_items()
    
    def stack_nearby_items(self):
        """Stack nearby items of the same type"""
        stacking_distance = 16  # Pixels
        
        for i, item1 in enumerate(self.item_drops):
            if item1['count'] >= 64:  # Already at max stack
                continue
                
            for j, item2 in enumerate(self.item_drops):
                if i >= j or item2['count'] >= 64:  # Skip same item or full stacks
                    continue
                
                if item1['type'] != item2['type']:  # Different item types
                    continue
                
                # Check distance
                distance = ((item1['x'] - item2['x']) ** 2 + (item1['y'] - item2['y']) ** 2) ** 0.5
                if distance <= stacking_distance:
                    # Stack items
                    total_count = item1['count'] + item2['count']
                    if total_count <= 64:
                        # Merge completely
                        item1['count'] = total_count
                        self.item_drops.remove(item2)
                        break  # Break inner loop since we modified the list
                    else:
                        # Partial merge
                        item1['count'] = 64
                        item2['count'] = total_count - 64
    
    def find_spawn_position(self):
        """Find a safe spawn position on the surface"""
        spawn_x = 0  # Spawn at world origin
        
        # Ensure spawn chunk is loaded
        self.load_chunk(0)
        
        # Find surface at spawn location
        for y in range(WORLD_HEIGHT):
            if self.get_block(spawn_x, y) != BLOCK_AIR:
                # Spawn 3 blocks above the surface
                return spawn_x * BLOCK_SIZE, (y - 3) * BLOCK_SIZE
        
        # Fallback if no surface found
        return spawn_x * BLOCK_SIZE, SURFACE_LEVEL * BLOCK_SIZE
    
    def get_loaded_chunks(self):
        """Get list of loaded chunk coordinates"""
        return list(self.chunks.keys())
    
    def save_all_chunks(self):
        """Save all loaded chunks"""
        for chunk in self.chunks.values():
            self.save_chunk(chunk)
        
        # Save world metadata
        self.save_world_data()
    
    def cleanup(self):
        """Clean up world resources and save data"""
        self.save_all_chunks()
        print(f"World saved to {self.save_dir}")