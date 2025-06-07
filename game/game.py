import pygame
import sys
from .constants import *
from .world import World
from .player import Player
from .camera import Camera
from .renderer import Renderer

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("2D Minecraft Survival")
        self.clock = pygame.time.Clock()
        
        # Initialize game objects
        self.world = World()
        self.player = Player(WORLD_WIDTH * BLOCK_SIZE // 2, 0)  # Start in middle of world
        self.camera = Camera()
        self.renderer = Renderer(self.screen)
        
        # Find a good spawn position (on surface)
        spawn_x = WORLD_WIDTH // 2
        for y in range(WORLD_HEIGHT):
            if self.world.get_block(spawn_x, y) != BLOCK_AIR:
                self.player.y = (y - 2) * BLOCK_SIZE
                break
        
        self.selected_block = BLOCK_DIRT
        self.running = True
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                # Block selection
                if event.key == pygame.K_1:
                    self.selected_block = BLOCK_DIRT
                elif event.key == pygame.K_2:
                    self.selected_block = BLOCK_STONE
                elif event.key == pygame.K_3:
                    self.selected_block = BLOCK_GRASS
                elif event.key == pygame.K_4:
                    self.selected_block = BLOCK_SAND
                elif event.key == pygame.K_5:
                    self.selected_block = BLOCK_WATER
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                if event.button == 1:  # Left click - mine
                    self.player.mine_block(self.world, mouse_x, mouse_y, 
                                         self.camera.x, self.camera.y)
                
                elif event.button == 3:  # Right click - place
                    self.player.place_block(self.world, mouse_x, mouse_y,
                                          self.camera.x, self.camera.y, 
                                          self.selected_block)
    
    def update(self):
        """Update game state"""
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update(self.world)
        self.camera.update(self.player)
    
    def draw(self):
        """Draw everything"""
        self.screen.fill(BLACK)
        
        # Draw world and player
        self.renderer.draw_world(self.world, self.camera)
        self.player.draw(self.screen, self.camera.x, self.camera.y)
        
        # Draw UI
        self.renderer.draw_ui(self.player)
        
        # Draw selected block indicator
        block_name = self.renderer.get_block_name(self.selected_block)
        selected_text = self.renderer.font.render(f"Selected: {block_name}", True, WHITE)
        self.screen.blit(selected_text, (SCREEN_WIDTH - 200, 10))
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)