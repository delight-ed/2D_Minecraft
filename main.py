import pygame
import sys
from src.game import Game
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("2D Minecraft")
    clock = pygame.time.Clock()
    
    game = Game(screen)
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)
        
        game.update(dt)
        game.render()
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()