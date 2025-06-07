import pygame
import os
from .constants import *

class TextureManager:
    def __init__(self):
        self.textures = {}
        self.block_size = BLOCK_SIZE
        self.assets_path = "game/assets"
        self.load_textures()
    
    def load_textures(self):
        """Load all Minecraft textures"""
        # Define texture mappings from block types to texture file paths
        texture_mappings = {
            # Blocks
            BLOCK_DIRT: "assets/minecraft/textures/block/dirt.png",
            BLOCK_GRASS: "assets/minecraft/textures/block/grass_block_top.png",
            BLOCK_STONE: "assets/minecraft/textures/block/stone.png",
            BLOCK_WATER: "assets/minecraft/textures/block/water_still.png",
            BLOCK_SAND: "assets/minecraft/textures/block/sand.png",
            BLOCK_WOOD: "assets/minecraft/textures/block/oak_log_top.png",
            BLOCK_LEAVES: "assets/minecraft/textures/block/oak_leaves.png",
            BLOCK_COAL: "assets/minecraft/textures/block/coal_ore.png",
            BLOCK_IRON: "assets/minecraft/textures/block/iron_ore.png",
            
            # Items
            ITEM_STICK: "assets/minecraft/textures/item/stick.png",
            ITEM_CRAFTING_TABLE: "assets/minecraft/textures/block/crafting_table_top.png",
            ITEM_WOODEN_PICKAXE: "assets/minecraft/textures/item/wooden_pickaxe.png",
        }
        
        # Load each texture
        for item_type, texture_path in texture_mappings.items():
            full_path = os.path.join("game", texture_path)
            if os.path.exists(full_path):
                try:
                    # Load and scale texture to block size
                    original_texture = pygame.image.load(full_path).convert_alpha()
                    scaled_texture = pygame.transform.scale(original_texture, (self.block_size, self.block_size))
                    self.textures[item_type] = scaled_texture
                    print(f"Loaded texture for {item_type}: {texture_path}")
                except Exception as e:
                    print(f"Error loading texture {texture_path}: {e}")
                    self.create_fallback_texture(item_type)
            else:
                print(f"Texture not found: {full_path}")
                self.create_fallback_texture(item_type)
        
        # Load special textures
        self.load_special_textures()
    
    def load_special_textures(self):
        """Load special textures that need custom handling"""
        # Grass block side texture (for 2D side view)
        grass_side_path = os.path.join("game", "assets/minecraft/textures/block/grass_block_side.png")
        if os.path.exists(grass_side_path):
            try:
                original = pygame.image.load(grass_side_path).convert_alpha()
                self.textures[f"{BLOCK_GRASS}_side"] = pygame.transform.scale(original, (self.block_size, self.block_size))
            except Exception as e:
                print(f"Error loading grass side texture: {e}")
        
        # Wood log side texture
        wood_side_path = os.path.join("game", "assets/minecraft/textures/block/oak_log.png")
        if os.path.exists(wood_side_path):
            try:
                original = pygame.image.load(wood_side_path).convert_alpha()
                self.textures[f"{BLOCK_WOOD}_side"] = pygame.transform.scale(original, (self.block_size, self.block_size))
            except Exception as e:
                print(f"Error loading wood side texture: {e}")
    
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
        
        surface.fill(color)
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
    
    def has_texture(self, item_type):
        """Check if texture exists for item type"""
        return item_type in self.textures