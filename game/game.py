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

class Game:
    def __init__(self):
        pygame.init()
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
        
        # Menu system
        self.main_menu = MainMenu(self.screen)
        self.settings_menu = SettingsMenu(self.screen, self.keybinds)
        
        # Game objects (initialized when starting game)
        self.world = None
        self.player = None
        self.camera = None
        self.renderer = None
        self.inventory_gui = None
        
        print("Game initialized!")
    
    def load_settings(self):
        """Load settings from file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    keybinds = settings.get('keybinds', DEFAULT_KEYBINDS.copy())
                    print("Settings loaded successfully!")
                    return keybinds
            except Exception as e:
                print(f"Error loading settings: {e}")
        
        # Return default settings if file doesn't exist or error occurred
        return DEFAULT_KEYBINDS.copy()
    
    def save_settings(self):
        """Save settings to file"""
        try:
            settings = {
                'keybinds': self.keybinds
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            print("Settings saved successfully!")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def init_game_world(self):
        """Initialize the game world and objects"""
        print("Generating world...")
        self.world = World()
        print("World generated!")
        
        # Find proper spawn position
        spawn_x, spawn_y = self.world.find_spawn_position()
        print(f"Spawn position: {spawn_x}, {spawn_y}")
        
        self.player = Player(spawn_x, spawn_y, self.keybinds)
        self.camera = Camera()
        self.renderer = Renderer(self.screen)
        self.inventory_gui = InventoryGUI(self.screen)
        
        print("Game world initialized!")
    
    def handle_menu_events(self):
        """Handle events in menu state"""
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
    
    def handle_settings_events(self):
        """Handle events in settings state"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            action = self.settings_menu.handle_event(event)
            if action == 'back':
                self.keybinds = self.settings_menu.get_keybinds()
                self.save_settings()  # Save settings when leaving settings menu
                self.state = STATE_MENU
    
    def handle_game_events(self):
        """Handle events in game state"""
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
        # Only update player movement if inventory is closed
        if not self.inventory_gui.is_open:
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
        
        self.player.update(self.world)
        self.player.pickup_items(self.world)
        self.camera.update(self.player)
        self.world.update_item_drops()
    
    def draw_menu(self):
        """Draw menu state"""
        self.main_menu.draw()
    
    def draw_settings(self):
        """Draw settings state"""
        self.settings_menu.draw()
    
    def draw_game(self):
        """Draw game state"""
        self.screen.fill((135, 206, 235))  # Sky blue background
        
        # Draw world and player
        self.renderer.draw_world(self.world, self.camera)
        self.player.draw(self.screen, self.camera.x, self.camera.y)
        
        # Draw UI
        self.renderer.draw_ui(self.player)
        
        # Draw inventory GUI on top
        self.inventory_gui.draw(self.player)
    
    def run(self):
        """Main game loop"""
        while self.running:
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
        
        # Save world and settings before quitting
        if self.world:
            self.world.cleanup()
        self.save_settings()
        
        pygame.quit()
        sys.exit()