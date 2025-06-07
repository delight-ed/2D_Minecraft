import pygame
import sys
from .constants import *
from .world import World
from .player import Player
from .camera import Camera
from .renderer import Renderer
from .inventory import InventoryGUI

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("2D Minecraft Survival")
        self.clock = pygame.time.Clock()
        
        # Initialize game objects
        print("Generating world...")
        self.world = World()
        print("World generated!")
        
        # Find proper spawn position
        spawn_x, spawn_y = self.world.find_spawn_position()
        print(f"Spawn position: {spawn_x}, {spawn_y}")
        
        self.player = Player(spawn_x, spawn_y)
        self.camera = Camera()
        self.renderer = Renderer(self.screen)
        self.inventory_gui = InventoryGUI(self.screen)
        
        self.running = True
        print("Game initialized!")
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                # Hotbar selection
                if pygame.K_1 <= event.key <= pygame.K_9:
                    slot = event.key - pygame.K_1
                    self.player.select_hotbar_slot(slot)
                
                # Toggle inventory
                elif event.key == pygame.K_e:
                    self.inventory_gui.toggle()
                
                # Quit game
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if clicking in inventory first
                if self.inventory_gui.handle_click(event.pos[0], event.pos[1], self.player):
                    continue
                
                # Only handle world interactions if inventory is closed
                if not self.inventory_gui.is_open:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    if event.button == 1:  # Left click - mine
                        self.player.mine_block(self.world, mouse_x, mouse_y, 
                                             self.camera.x, self.camera.y)
                    
                    elif event.button == 3:  # Right click - place
                        self.player.place_block(self.world, mouse_x, mouse_y,
                                              self.camera.x, self.camera.y)
    
    def update(self):
        """Update game state"""
        # Only update player movement if inventory is closed
        if not self.inventory_gui.is_open:
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
        
        self.player.update(self.world)
        self.player.pickup_items(self.world)
        self.camera.update(self.player)
        self.world.update_item_drops()
    
    def draw(self):
        """Draw everything"""
        self.screen.fill((135, 206, 235))  # Sky blue background
        
        # Draw world and player
        self.renderer.draw_world(self.world, self.camera)
        self.player.draw(self.screen, self.camera.x, self.camera.y)
        
        # Draw UI
        self.renderer.draw_ui(self.player)
        
        # Draw inventory GUI on top
        self.inventory_gui.draw(self.player)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()