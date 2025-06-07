# Game constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Block size
BLOCK_SIZE = 32

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
GREEN = (34, 139, 34)
GRAY = (128, 128, 128)
BLUE = (30, 144, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 100, 0)
LIGHT_BROWN = (205, 133, 63)
DARK_GRAY = (64, 64, 64)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
LIGHT_GRAY = (192, 192, 192)
DARK_BLUE = (0, 0, 139)

# Block types
BLOCK_AIR = 0
BLOCK_DIRT = 1
BLOCK_GRASS = 2
BLOCK_STONE = 3
BLOCK_WATER = 4
BLOCK_SAND = 5
BLOCK_WOOD = 6
BLOCK_LEAVES = 7
BLOCK_COAL = 8
BLOCK_IRON = 9

# Block colors
BLOCK_COLORS = {
    BLOCK_AIR: None,
    BLOCK_DIRT: BROWN,
    BLOCK_GRASS: GREEN,
    BLOCK_STONE: GRAY,
    BLOCK_WATER: BLUE,
    BLOCK_SAND: YELLOW,
    BLOCK_WOOD: LIGHT_BROWN,
    BLOCK_LEAVES: DARK_GREEN,
    BLOCK_COAL: DARK_GRAY,
    BLOCK_IRON: (192, 192, 192)
}

# World settings
WORLD_WIDTH = 400
WORLD_HEIGHT = 150
SURFACE_LEVEL = 80
CHUNK_SIZE = 16  # Blocks per chunk
RENDER_DISTANCE = 8  # Chunks to render around player

# Biome types
BIOME_PLAINS = 0
BIOME_FOREST = 1
BIOME_DESERT = 2
BIOME_MOUNTAINS = 3

# Hotbar settings
HOTBAR_SIZE = 9
HOTBAR_SLOT_SIZE = 50
HOTBAR_MARGIN = 10

# Default keybinds
DEFAULT_KEYBINDS = {
    'move_left': 'a',
    'move_right': 'd',
    'jump': 'space',
    'inventory': 'e',
    'mine': 'left_click',
    'place': 'right_click'
}

# Game states
STATE_MENU = 0
STATE_PLAYING = 1
STATE_SETTINGS = 2