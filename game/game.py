import pygame
import sys
import json
import os
from .constants import *
from .world import World
from .player import Player
from .camera import Camera
from .renderer import Renderer
from .inventory import InventoryGUI
from .menu import MainMenu, SettingsMenu
from .texture_manager import TextureManager
from .error_handler import GameErrorHandler, PerformanceMonitor, safe_execute
from .utils import Timer

class Game:
    def __init__(self):
        pygame.init()
        
        # Initialize error handling
        self.error_handler = GameErrorHandler()
        self.performance_monitor = PerformanceMonitor(self.error_handler)
        
        # Override emergency save
        self.error_handler.emergency_save = self.emergency_save
        
        try:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("2D Minecraft Survival")
            self.clock = pygame.time.Clock()
            
            # Game state
            self.state = STATE_MENU
            self.running = True
            
            # Settings file path
            self.settings_file = "settings.json"
            
            # Load settings
            self.keybinds = self.load_settings()
            
            # Initialize texture manager
            self.texture_manager = TextureManager()
            
            # Menu system
            self.main_menu = MainMenu(self.screen)
            self.settings_menu = SettingsMenu(self.screen, self.keybinds)
            
            # Game objects (initialized when starting game)
            self.world = None
            self.player = None
            self.camera = None
            self.renderer = None
            self.inventory_gui = None
            
            # Performance tracking
            self.frame_timer = Timer()
            
            self.error_handler.log_info("Game initialized successfully", "Game.__init__")
            
        except Exception as e:
            self.error_handler.handle_critical_error(e, "Game.__init__")
            raise
    
    def load_settings(self):
        """Load settings from file"""
        def _load():
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    keybinds = settings.get('keybinds', DEFAULT_KEYBINDS.copy())
                    self.error_handler.log_info("Settings loaded successfully", "load_settings")
                    return keybinds
            return DEFAULT_KEYBINDS.copy()
        
        return safe_execute(_load, self.error_handler, "load_settings", DEFAULT_KEYBINDS.copy())
    
    def save_settings(self):
        """Save settings to file"""
        def _save():
            settings = {
                'keybinds': self.keybinds
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            self.error_handler.log_info("Settings saved successfully", "save_settings")
        
        safe_execute(_save, self.error_handler, "save_settings")
    
    def init_game_world(self):
        """Initialize the game world and objects"""
        try:
            self.error_handler.log_info("Generating world...", "init_game_world")
            self.world = World()
            self.error_handler.log_info("World generated!", "init_game_world")
            
            # Find proper spawn position
            spawn_x, spawn_y = self.world.find_spawn_position()
            self.error_handler.log_info(f"Spawn position: {spawn_x}, {spawn_y}", "init_game_world")
            
            self.player = Player(spawn_x, spawn_y, self.keybinds, self.texture_manager)
            self.camera = Camera()
            self.renderer = Renderer(self.screen, self.texture_manager)
            self.inventory_gui = InventoryGUI(self.screen, self.texture_manager)
            
            self.error_handler.log_info("Game world initialized!", "init_game_world")
            
        except Exception as e:
            self.error_handler.handle_critical_error(e, "init_game_world")
            raise
    
    def handle_menu_events(self):
        """Handle events in menu state"""
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                action = self.main_menu.handle_event(event)
                if action == 'play':
                    self.init_game_world()
                    self.state = STATE_PLAYING
                elif action == 'settings':
                    self.state = STATE_SETTINGS
                elif action == 'quit':
                    self.running = False
        except Exception as e:
            self.error_handler.log_error(e, "handle_menu_events")
    
    def handle_settings_events(self):
        """Handle events in settings state"""
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                action = self.settings_menu.handle_event(event)
                if action == 'back':
                    self.keybinds = self.settings_menu.get_keybinds()
                    self.save_settings()  # Save settings when leaving settings menu
                    self.state = STATE_MENU
        except Exception as e:
            self.error_handler.log_error(e, "handle_settings_events")
    
    def handle_game_events(self):
        """Handle events in game state"""
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.KEYDOWN:
                    # Hotbar selection
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        slot = event.key - pygame.K_1
                        self.player.select_hotbar_slot(slot)
                    
                    # Toggle inventory
                    elif event.key == self.get_key_from_keybind('inventory'):
                        self.inventory_gui.toggle()
                    
                    # Return to menu
                    elif event.key == pygame.K_ESCAPE:
                        if self.inventory_gui.is_open:
                            self.inventory_gui.toggle()
                        else:
                            # Save world before returning to menu
                            if self.world:
                                self.world.cleanup()
                            self.state = STATE_MENU
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if clicking in inventory first
                    if self.inventory_gui.handle_click(event.pos[0], event.pos[1], self.player):
                        continue
                    
                    # Only handle world interactions if inventory is closed
                    if not self.inventory_gui.is_open:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        
                        if event.button == 1 and self.keybinds['mine'] == 'left_click':  # Left click - mine
                            self.player.mine_block(self.world, mouse_x, mouse_y, 
                                                 self.camera.x, self.camera.y)
                        
                        elif event.button == 3 and self.keybinds['place'] == 'right_click':  # Right click - place
                            self.player.place_block(self.world, mouse_x, mouse_y,
                                                  self.camera.x, self.camera.y)
        except Exception as e:
            self.error_handler.log_error(e, "handle_game_events")
    
    def get_key_from_keybind(self, keybind_name):
        """Convert keybind string to pygame key constant"""
        key_name = self.keybinds.get(keybind_name, '')
        if key_name == 'space':
            return pygame.K_SPACE
        elif len(key_name) == 1:
            return getattr(pygame, f'K_{key_name}', pygame.K_UNKNOWN)
        return pygame.K_UNKNOWN
    
    def update_game(self):
        """Update game state"""
        try:
            # Only update player movement if inventory is closed
            if not self.inventory_gui.is_open:
                keys = pygame.key.get_pressed()
                self.player.handle_input(keys)
            
            self.player.update(self.world)
            self.player.pickup_items(self.world)
            self.camera.update(self.player)
            self.world.update_item_drops()
        except Exception as e:
            self.error_handler.log_error(e, "update_game")
    
    def draw_menu(self):
        """Draw menu state"""
        try:
            self.main_menu.draw()
        except Exception as e:
            self.error_handler.log_error(e, "draw_menu")
    
    def draw_settings(self):
        """Draw settings state"""
        try:
            self.settings_menu.draw()
        except Exception as e:
            self.error_handler.log_error(e, "draw_settings")
    
    def draw_game(self):
        """Draw game state"""
        try:
            self.screen.fill((135, 206, 235))  # Sky blue background
            
            # Draw world and player
            self.renderer.draw_world(self.world, self.camera)
            self.player.draw(self.screen, self.camera.x, self.camera.y)
            
            # Draw UI
            self.renderer.draw_ui(self.player)
            
            # Draw inventory GUI on top
            self.inventory_gui.draw(self.player)
        except Exception as e:
            self.error_handler.log_error(e, "draw_game")
    
    def emergency_save(self):
        """Emergency save function for critical errors"""
        try:
            if self.world:
                self.world.save_all_chunks()
            self.save_settings()
            self.error_handler.log_info("Emergency save completed", "emergency_save")
        except Exception as e:
            self.error_handler.log_error(e, "emergency_save")
    
    def run(self):
        """Main game loop"""
        try:
            while self.running:
                frame_start = pygame.time.get_ticks()
                
                if self.state == STATE_MENU:
                    self.handle_menu_events()
                    self.draw_menu()
                elif self.state == STATE_SETTINGS:
                    self.handle_settings_events()
                    self.draw_settings()
                elif self.state == STATE_PLAYING:
                    self.handle_game_events()
                    self.update_game()
                    self.draw_game()
                
                pygame.display.flip()
                self.clock.tick(FPS)
                
                # Performance monitoring
                frame_time = pygame.time.get_ticks() - frame_start
                self.performance_monitor.record_frame_time(frame_time)
            
            # Save world and settings before quitting
            if self.world:
                self.world.cleanup()
            self.save_settings()
            
        except Exception as e:
            self.error_handler.handle_critical_error(e, "main_game_loop")
        finally:
            pygame.quit()
            sys.exit()