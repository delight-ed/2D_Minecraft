import pygame
import os
import zipfile
import json
from .constants import *

class TextureManager:
    def __init__(self):
        self.textures = {}
        self.block_size = BLOCK_SIZE
        self.assets_path = "game/assets"
        self.texture_pack_path = "game/assets/VanillaDefault 1.21.5.zip"
        
        # Comprehensive block and item mappings
        self.block_mappings = {
            BLOCK_DIRT: "dirt",
            BLOCK_GRASS: "grass_block",
            BLOCK_STONE: "stone",
            BLOCK_WATER: "water_still",
            BLOCK_SAND: "sand",
            BLOCK_WOOD: "oak_log",
            BLOCK_LEAVES: "oak_leaves",
            BLOCK_COAL: "coal_ore",
            BLOCK_IRON: "iron_ore",
            
            # Items
            ITEM_STICK: "stick",
            ITEM_CRAFTING_TABLE: "crafting_table",
            ITEM_WOODEN_PICKAXE: "wooden_pickaxe",
        }
        
        # Alternative names to try if primary doesn't work
        self.alternative_mappings = {
            BLOCK_WATER: ["water", "water_flow", "water_still"],
            BLOCK_WOOD: ["oak_log", "log", "wood"],
            BLOCK_LEAVES: ["oak_leaves", "leaves"],
            BLOCK_COAL: ["coal_ore", "coal_block"],
            BLOCK_IRON: ["iron_ore", "iron_block"],
        }
        
        self.load_textures()
    
    def load_textures(self):
        """Load all textures from the ZIP file"""
        if os.path.exists(self.texture_pack_path):
            self.load_from_zip()
        else:
            print(f"Texture pack not found: {self.texture_pack_path}")
            self.create_fallback_textures()
    
    def load_from_zip(self):
        """Load textures from ZIP file with comprehensive mapping"""
        try:
            with zipfile.ZipFile(self.texture_pack_path, 'r') as zip_file:
                # Get list of all files in the ZIP
                file_list = zip_file.namelist()
                
                # Try to find and load mapping file first
                mapping_data = self.load_mapping_file(zip_file, file_list)
                
                # Load block textures
                for block_id, minecraft_name in self.block_mappings.items():
                    self.load_texture_from_zip(zip_file, file_list, block_id, minecraft_name, "block", mapping_data)
                
                # Load item textures
                item_types = [ITEM_STICK, ITEM_CRAFTING_TABLE, ITEM_WOODEN_PICKAXE]
                for item_id in item_types:
                    minecraft_name = self.block_mappings.get(item_id)
                    if minecraft_name:
                        self.load_texture_from_zip(zip_file, file_list, item_id, minecraft_name, "item", mapping_data)
                
                # Load special textures
                self.load_special_textures_from_zip(zip_file, file_list)
                
                # Load breaking animation textures
                self.load_breaking_textures_from_zip(zip_file, file_list)
                
                # Load player skin
                self.load_player_skin_from_zip(zip_file, file_list)
                
                print(f"Loaded {len(self.textures)} textures from ZIP file")
        
        except Exception as e:
            print(f"Error loading from ZIP: {e}")
            self.create_fallback_textures()
    
    def load_mapping_file(self, zip_file, file_list):
        """Try to load mapping file from the ZIP"""
        mapping_files = [
            "assets/minecraft/blockstates/",
            "assets/minecraft/models/block/",
            "assets/minecraft/models/item/",
            "pack.mcmeta"
        ]
        
        # For now, we'll use our own mapping since Minecraft's structure is complex
        # In a real implementation, you'd parse the JSON files to get proper mappings
        return None
    
    def load_texture_from_zip(self, zip_file, file_list, item_id, minecraft_name, texture_type, mapping_data=None):
        """Load a specific texture from ZIP file with multiple fallbacks"""
        # Try different possible paths and names
        names_to_try = [minecraft_name]
        
        # Add alternative names if available
        if item_id in self.alternative_mappings:
            names_to_try.extend(self.alternative_mappings[item_id])
        
        for name in names_to_try:
            possible_paths = [
                f"assets/minecraft/textures/{texture_type}/{name}.png",
                f"minecraft/textures/{texture_type}/{name}.png",
                f"textures/{texture_type}/{name}.png",
                f"{texture_type}/{name}.png",
                f"{name}.png",
                f"assets/minecraft/textures/blocks/{name}.png",  # Legacy path
                f"assets/minecraft/textures/items/{name}.png",   # Legacy path
            ]
            
            for path in possible_paths:
                if path in file_list:
                    try:
                        # Extract and load the texture
                        texture_data = zip_file.read(path)
                        
                        # Create a temporary file-like object
                        import io
                        texture_file = io.BytesIO(texture_data)
                        
                        # Load the image
                        original_texture = pygame.image.load(texture_file).convert_alpha()
                        scaled_texture = pygame.transform.scale(original_texture, (self.block_size, self.block_size))
                        
                        self.textures[item_id] = scaled_texture
                        print(f"Loaded {name} from {path}")
                        return True
                        
                    except Exception as e:
                        print(f"Error loading {path}: {e}")
                        continue
        
        # If not found, create fallback
        print(f"Texture not found for {minecraft_name}, creating fallback")
        self.create_fallback_texture(item_id)
        return False
    
    def load_breaking_textures_from_zip(self, zip_file, file_list):
        """Load breaking animation textures from ZIP file"""
        self.breaking_textures = {}
        
        # Try to load destroy stage textures from the ZIP
        for stage in range(10):
            stage_names = [
                f"destroy_stage_{stage}",
                f"destroy_{stage}",
                f"breaking_{stage}",
                f"crack_{stage}"
            ]
            
            for stage_name in stage_names:
                possible_paths = [
                    f"assets/minecraft/textures/block/{stage_name}.png",
                    f"minecraft/textures/block/{stage_name}.png",
                    f"textures/block/{stage_name}.png",
                    f"block/{stage_name}.png",
                    f"{stage_name}.png",
                    f"assets/minecraft/textures/blocks/{stage_name}.png"  # Legacy
                ]
                
                loaded = False
                for path in possible_paths:
                    if path in file_list:
                        try:
                            import io
                            texture_data = zip_file.read(path)
                            texture_file = io.BytesIO(texture_data)
                            original = pygame.image.load(texture_file).convert_alpha()
                            scaled = pygame.transform.scale(original, (self.block_size, self.block_size))
                            self.breaking_textures[stage] = scaled
                            print(f"Loaded breaking stage {stage} from {path}")
                            loaded = True
                            break
                        except Exception as e:
                            print(f"Error loading breaking texture {path}: {e}")
                
                if loaded:
                    break
        
        # If we couldn't load breaking textures from ZIP, create fallback ones
        if not self.breaking_textures:
            print("Creating fallback breaking animation textures")
            self.create_breaking_animation_textures()
    
    def load_special_textures_from_zip(self, zip_file, file_list):
        """Load special texture variants from ZIP"""
        # Grass block side texture
        grass_side_paths = [
            "assets/minecraft/textures/block/grass_block_side.png",
            "minecraft/textures/block/grass_block_side.png",
            "textures/block/grass_block_side.png",
            "block/grass_block_side.png",
            "assets/minecraft/textures/blocks/grass_side.png"  # Legacy
        ]
        
        for path in grass_side_paths:
            if path in file_list:
                try:
                    import io
                    texture_data = zip_file.read(path)
                    texture_file = io.BytesIO(texture_data)
                    original = pygame.image.load(texture_file).convert_alpha()
                    self.textures[f"{BLOCK_GRASS}_side"] = pygame.transform.scale(original, (self.block_size, self.block_size))
                    print("Loaded grass side texture")
                    break
                except Exception as e:
                    print(f"Error loading grass side texture: {e}")
        
        # Wood log side texture
        wood_side_paths = [
            "assets/minecraft/textures/block/oak_log.png",
            "minecraft/textures/block/oak_log.png",
            "textures/block/oak_log.png",
            "block/oak_log.png",
            "assets/minecraft/textures/blocks/log_oak.png"  # Legacy
        ]
        
        for path in wood_side_paths:
            if path in file_list:
                try:
                    import io
                    texture_data = zip_file.read(path)
                    texture_file = io.BytesIO(texture_data)
                    original = pygame.image.load(texture_file).convert_alpha()
                    self.textures[f"{BLOCK_WOOD}_side"] = pygame.transform.scale(original, (self.block_size, self.block_size))
                    print("Loaded wood side texture")
                    break
                except Exception as e:
                    print(f"Error loading wood side texture: {e}")
        
        # Grass block top texture
        grass_top_paths = [
            "assets/minecraft/textures/block/grass_block_top.png",
            "minecraft/textures/block/grass_block_top.png",
            "textures/block/grass_block_top.png",
            "block/grass_block_top.png",
            "assets/minecraft/textures/blocks/grass_top.png"  # Legacy
        ]
        
        for path in grass_top_paths:
            if path in file_list:
                try:
                    import io
                    texture_data = zip_file.read(path)
                    texture_file = io.BytesIO(texture_data)
                    original = pygame.image.load(texture_file).convert_alpha()
                    self.textures[f"{BLOCK_GRASS}_top"] = pygame.transform.scale(original, (self.block_size, self.block_size))
                    print("Loaded grass top texture")
                    break
                except Exception as e:
                    print(f"Error loading grass top texture: {e}")
    
    def load_player_skin_from_zip(self, zip_file, file_list):
        """Load player skin from ZIP file"""
        steve_paths = [
            "assets/minecraft/textures/entity/player/wide/steve.png",
            "minecraft/textures/entity/player/wide/steve.png",
            "textures/entity/player/wide/steve.png",
            "entity/player/wide/steve.png",
            "player/wide/steve.png",
            "steve.png",
            "assets/minecraft/textures/entity/steve.png"  # Alternative path
        ]
        
        for path in steve_paths:
            if path in file_list:
                try:
                    import io
                    texture_data = zip_file.read(path)
                    texture_file = io.BytesIO(texture_data)
                    self.player_skin = pygame.image.load(texture_file).convert_alpha()
                    print("Loaded Steve skin from ZIP")
                    return
                except Exception as e:
                    print(f"Error loading Steve skin: {e}")
        
        print("Steve skin not found in ZIP")
        self.player_skin = None
    
    def create_fallback_textures(self):
        """Create fallback textures for all items"""
        for item_id in self.block_mappings.keys():
            self.create_fallback_texture(item_id)
        
        # Create fallback breaking textures
        self.create_breaking_animation_textures()
    
    def create_fallback_texture(self, item_type):
        """Create a fallback texture if the original can't be loaded"""
        surface = pygame.Surface((self.block_size, self.block_size))
        
        # Use the original color scheme as fallback
        if item_type in BLOCK_COLORS:
            color = BLOCK_COLORS[item_type]
        elif item_type in ITEM_COLORS:
            color = ITEM_COLORS[item_type]
        else:
            color = (200, 200, 200)
        
        if color:
            surface.fill(color)
            # Add some texture pattern for better visual distinction
            for i in range(0, self.block_size, 4):
                for j in range(0, self.block_size, 4):
                    if (i + j) % 8 == 0:
                        darker_color = tuple(max(0, c - 20) for c in color)
                        pygame.draw.rect(surface, darker_color, (i, j, 2, 2))
            
            pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 1)
        
        self.textures[item_type] = surface
    
    def get_texture(self, item_type, variant=None):
        """Get texture for an item type"""
        if variant:
            texture_key = f"{item_type}_{variant}"
            if texture_key in self.textures:
                return self.textures[texture_key]
        
        return self.textures.get(item_type, None)
    
    def get_scaled_texture(self, item_type, size, variant=None):
        """Get texture scaled to specific size"""
        texture = self.get_texture(item_type, variant)
        if texture and size != self.block_size:
            return pygame.transform.scale(texture, (size, size))
        return texture
    
    def get_player_texture(self):
        """Get player skin texture"""
        return getattr(self, 'player_skin', None)
    
    def has_texture(self, item_type):
        """Check if texture exists for item type"""
        return item_type in self.textures
    
    def create_breaking_animation_textures(self):
        """Create block breaking animation textures"""
        if not hasattr(self, 'breaking_textures'):
            self.breaking_textures = {}
        
        # Create 10 stages of breaking animation if not loaded from ZIP
        for stage in range(10):
            if stage not in self.breaking_textures:
                surface = pygame.Surface((self.block_size, self.block_size), pygame.SRCALPHA)
                
                # Create crack pattern that gets more intense
                crack_intensity = (stage + 1) / 10.0
                crack_color = (0, 0, 0, int(150 * crack_intensity))
                
                # Draw crack lines in a more realistic pattern
                num_cracks = int(3 + stage * 0.7)
                for i in range(num_cracks):
                    # Vertical cracks
                    x = int(self.block_size * (i + 0.5) / num_cracks)
                    pygame.draw.line(surface, crack_color, 
                                   (x, 0), (x, self.block_size), 
                                   max(1, int(2 * crack_intensity)))
                    
                    # Horizontal cracks
                    y = int(self.block_size * (i + 0.5) / num_cracks)
                    pygame.draw.line(surface, crack_color, 
                                   (0, y), (self.block_size, y), 
                                   max(1, int(2 * crack_intensity)))
                    
                    # Diagonal cracks for later stages
                    if stage > 5:
                        pygame.draw.line(surface, crack_color,
                                       (0, 0), (self.block_size, self.block_size),
                                       max(1, int(crack_intensity)))
                        pygame.draw.line(surface, crack_color,
                                       (self.block_size, 0), (0, self.block_size),
                                       max(1, int(crack_intensity)))
                
                self.breaking_textures[stage] = surface
    
    def get_breaking_texture(self, stage):
        """Get breaking animation texture for given stage (0-9)"""
        if not hasattr(self, 'breaking_textures'):
            self.create_breaking_animation_textures()
        
        return self.breaking_textures.get(stage, None)