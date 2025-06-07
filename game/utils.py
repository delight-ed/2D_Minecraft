"""
Utility functions for the game
"""
import pygame
import math
from .constants import *

def clamp(value, min_value, max_value):
    """Clamp a value between min and max"""
    return max(min_value, min(max_value, value))

def distance(x1, y1, x2, y2):
    """Calculate distance between two points"""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def world_to_screen(world_x, world_y, camera_x, camera_y):
    """Convert world coordinates to screen coordinates"""
    return world_x - camera_x, world_y - camera_y

def screen_to_world(screen_x, screen_y, camera_x, camera_y):
    """Convert screen coordinates to world coordinates"""
    return screen_x + camera_x, screen_y + camera_y

def get_block_at_position(x, y):
    """Get block coordinates from world position"""
    return int(x // BLOCK_SIZE), int(y // BLOCK_SIZE)

def is_point_in_rect(point_x, point_y, rect_x, rect_y, rect_width, rect_height):
    """Check if a point is inside a rectangle"""
    return (rect_x <= point_x <= rect_x + rect_width and 
            rect_y <= point_y <= rect_y + rect_height)

def lerp(start, end, factor):
    """Linear interpolation between two values"""
    return start + (end - start) * factor

def create_gradient_surface(width, height, start_color, end_color, vertical=True):
    """Create a surface with a gradient"""
    surface = pygame.Surface((width, height))
    
    if vertical:
        for y in range(height):
            factor = y / height
            color = [
                int(lerp(start_color[i], end_color[i], factor))
                for i in range(3)
            ]
            pygame.draw.line(surface, color, (0, y), (width, y))
    else:
        for x in range(width):
            factor = x / width
            color = [
                int(lerp(start_color[i], end_color[i], factor))
                for i in range(3)
            ]
            pygame.draw.line(surface, color, (x, 0), (x, height))
    
    return surface

def draw_text_with_shadow(surface, font, text, x, y, text_color=WHITE, shadow_color=BLACK, shadow_offset=(1, 1)):
    """Draw text with a shadow effect"""
    # Draw shadow
    shadow_text = font.render(text, True, shadow_color)
    surface.blit(shadow_text, (x + shadow_offset[0], y + shadow_offset[1]))
    
    # Draw main text
    main_text = font.render(text, True, text_color)
    surface.blit(main_text, (x, y))
    
    return main_text.get_rect(x=x, y=y)

def safe_divide(numerator, denominator, default=0):
    """Safely divide two numbers, returning default if denominator is zero"""
    return numerator / denominator if denominator != 0 else default

def normalize_angle(angle):
    """Normalize an angle to be between 0 and 2π"""
    while angle < 0:
        angle += 2 * math.pi
    while angle >= 2 * math.pi:
        angle -= 2 * math.pi
    return angle

def get_block_name(block_type):
    """Get human-readable block name"""
    names = {
        BLOCK_DIRT: "Dirt",
        BLOCK_GRASS: "Grass Block",
        BLOCK_STONE: "Stone",
        BLOCK_WATER: "Water",
        BLOCK_SAND: "Sand",
        BLOCK_WOOD: "Oak Log",
        BLOCK_LEAVES: "Oak Leaves",
        BLOCK_COAL: "Coal Ore",
        BLOCK_IRON: "Iron Ore",
        ITEM_STICK: "Stick",
        ITEM_CRAFTING_TABLE: "Crafting Table",
        ITEM_WOODEN_PICKAXE: "Wooden Pickaxe"
    }
    return names.get(block_type, "Unknown")

def format_number(number):
    """Format a number with appropriate suffixes (K, M, etc.)"""
    if number >= 1000000:
        return f"{number / 1000000:.1f}M"
    elif number >= 1000:
        return f"{number / 1000:.1f}K"
    else:
        return str(number)

class Timer:
    """Simple timer class for tracking elapsed time"""
    def __init__(self):
        self.start_time = pygame.time.get_ticks()
        self.paused_time = 0
        self.is_paused = False
    
    def reset(self):
        """Reset the timer"""
        self.start_time = pygame.time.get_ticks()
        self.paused_time = 0
        self.is_paused = False
    
    def pause(self):
        """Pause the timer"""
        if not self.is_paused:
            self.is_paused = True
            self.pause_start = pygame.time.get_ticks()
    
    def resume(self):
        """Resume the timer"""
        if self.is_paused:
            self.paused_time += pygame.time.get_ticks() - self.pause_start
            self.is_paused = False
    
    def get_elapsed(self):
        """Get elapsed time in milliseconds"""
        if self.is_paused:
            return self.pause_start - self.start_time - self.paused_time
        else:
            return pygame.time.get_ticks() - self.start_time - self.paused_time
    
    def get_elapsed_seconds(self):
        """Get elapsed time in seconds"""
        return self.get_elapsed() / 1000.0

class FPSCounter:
    """FPS counter for performance monitoring"""
    def __init__(self, sample_size=60):
        self.sample_size = sample_size
        self.frame_times = []
        self.last_time = pygame.time.get_ticks()
    
    def update(self):
        """Update the FPS counter"""
        current_time = pygame.time.get_ticks()
        frame_time = current_time - self.last_time
        self.last_time = current_time
        
        self.frame_times.append(frame_time)
        if len(self.frame_times) > self.sample_size:
            self.frame_times.pop(0)
    
    def get_fps(self):
        """Get current FPS"""
        if not self.frame_times:
            return 0
        
        average_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1000.0 / average_frame_time if average_frame_time > 0 else 0
    
    def get_frame_time(self):
        """Get average frame time in milliseconds"""
        if not self.frame_times:
            return 0
        return sum(self.frame_times) / len(self.frame_times)