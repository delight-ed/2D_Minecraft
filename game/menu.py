import pygame
from .constants import *

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        self.buttons = []
        self.selected_button = 0
        self.setup_buttons()
        
    def setup_buttons(self):
        """Setup menu buttons"""
        button_width = 300
        button_height = 60
        button_x = (SCREEN_WIDTH - button_width) // 2
        start_y = SCREEN_HEIGHT // 2 - 50
        
        self.buttons = [
            {'text': 'Play Game', 'rect': pygame.Rect(button_x, start_y, button_width, button_height), 'action': 'play'},
            {'text': 'Settings', 'rect': pygame.Rect(button_x, start_y + 80, button_width, button_height), 'action': 'settings'},
            {'text': 'Quit', 'rect': pygame.Rect(button_x, start_y + 160, button_width, button_height), 'action': 'quit'}
        ]
    
    def handle_event(self, event):
        """Handle menu events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_button = (self.selected_button - 1) % len(self.buttons)
            elif event.key == pygame.K_DOWN:
                self.selected_button = (self.selected_button + 1) % len(self.buttons)
            elif event.key == pygame.K_RETURN:
                return self.buttons[self.selected_button]['action']
        
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            for i, button in enumerate(self.buttons):
                if button['rect'].collidepoint(mouse_pos):
                    self.selected_button = i
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons:
                    if button['rect'].collidepoint(mouse_pos):
                        return button['action']
        
        return None
    
    def draw(self):
        """Draw the main menu"""
        # Background gradient
        for y in range(SCREEN_HEIGHT):
            color_value = int(135 + (y / SCREEN_HEIGHT) * 50)
            color = (color_value, color_value + 20, 255)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Title
        title_text = self.font_large.render("2D Minecraft", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        
        # Title shadow
        shadow_text = self.font_large.render("2D Minecraft", True, BLACK)
        shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH // 2 + 3, 153))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.font_small.render("Survival Edition", True, LIGHT_GRAY)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Buttons
        for i, button in enumerate(self.buttons):
            # Button background
            if i == self.selected_button:
                pygame.draw.rect(self.screen, (100, 100, 100), button['rect'])
                pygame.draw.rect(self.screen, WHITE, button['rect'], 3)
            else:
                pygame.draw.rect(self.screen, (60, 60, 60), button['rect'])
                pygame.draw.rect(self.screen, GRAY, button['rect'], 2)
            
            # Button text
            text_color = WHITE if i == self.selected_button else LIGHT_GRAY
            text = self.font_medium.render(button['text'], True, text_color)
            text_rect = text.get_rect(center=button['rect'].center)
            self.screen.blit(text, text_rect)
        
        # Instructions
        instructions = [
            "Use arrow keys or mouse to navigate",
            "Press Enter or click to select"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, LIGHT_GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80 + i * 25))
            self.screen.blit(text, text_rect)


class SettingsMenu:
    def __init__(self, screen, keybinds):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        self.keybinds = keybinds.copy()
        self.original_keybinds = keybinds.copy()
        self.selected_key = 0
        self.waiting_for_key = False
        self.key_names = list(self.keybinds.keys())
        
    def handle_event(self, event):
        """Handle settings menu events"""
        if self.waiting_for_key:
            if event.type == pygame.KEYDOWN:
                # Convert pygame key to string
                key_name = pygame.key.name(event.key)
                if key_name == 'space':
                    key_name = 'space'
                elif key_name == 'escape':
                    self.waiting_for_key = False
                    return None
                
                self.keybinds[self.key_names[self.selected_key]] = key_name
                self.waiting_for_key = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.keybinds[self.key_names[self.selected_key]] = 'left_click'
                elif event.button == 3:
                    self.keybinds[self.key_names[self.selected_key]] = 'right_click'
                self.waiting_for_key = False
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'back'
            elif event.key == pygame.K_UP:
                self.selected_key = (self.selected_key - 1) % len(self.key_names)
            elif event.key == pygame.K_DOWN:
                self.selected_key = (self.selected_key + 1) % len(self.key_names)
            elif event.key == pygame.K_RETURN:
                self.waiting_for_key = True
            elif event.key == pygame.K_r:
                # Reset to defaults
                self.keybinds = DEFAULT_KEYBINDS.copy()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                
                # Check keybind buttons
                start_y = 150
                for i, key_name in enumerate(self.key_names):
                    button_rect = pygame.Rect(400, start_y + i * 50, 200, 40)
                    if button_rect.collidepoint(mouse_pos):
                        self.selected_key = i
                        self.waiting_for_key = True
                        break
                
                # Check back button
                back_rect = pygame.Rect(50, SCREEN_HEIGHT - 100, 100, 50)
                if back_rect.collidepoint(mouse_pos):
                    return 'back'
                
                # Check reset button
                reset_rect = pygame.Rect(200, SCREEN_HEIGHT - 100, 150, 50)
                if reset_rect.collidepoint(mouse_pos):
                    self.keybinds = DEFAULT_KEYBINDS.copy()
        
        return None
    
    def get_keybinds(self):
        """Get current keybinds"""
        return self.keybinds
    
    def draw(self):
        """Draw the settings menu"""
        # Background
        self.screen.fill((40, 40, 40))
        
        # Title
        title_text = self.font_large.render("Settings - Key Bindings", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Instructions
        if self.waiting_for_key:
            instruction = "Press a key or mouse button to bind..."
            color = YELLOW
        else:
            instruction = "Use arrow keys to navigate, Enter to change, R to reset"
            color = LIGHT_GRAY
        
        instruction_text = self.font_small.render(instruction, True, color)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(instruction_text, instruction_rect)
        
        # Keybind list
        start_y = 150
        for i, key_name in enumerate(self.key_names):
            y_pos = start_y + i * 50
            
            # Key description
            description = key_name.replace('_', ' ').title()
            desc_text = self.font_medium.render(description + ":", True, WHITE)
            self.screen.blit(desc_text, (100, y_pos))
            
            # Current binding button
            current_key = self.keybinds[key_name]
            display_key = current_key.replace('_', ' ').title()
            
            button_rect = pygame.Rect(400, y_pos, 200, 40)
            
            # Highlight selected or waiting
            if i == self.selected_key:
                if self.waiting_for_key:
                    pygame.draw.rect(self.screen, YELLOW, button_rect)
                    pygame.draw.rect(self.screen, WHITE, button_rect, 3)
                else:
                    pygame.draw.rect(self.screen, (80, 80, 80), button_rect)
                    pygame.draw.rect(self.screen, WHITE, button_rect, 2)
            else:
                pygame.draw.rect(self.screen, (60, 60, 60), button_rect)
                pygame.draw.rect(self.screen, GRAY, button_rect, 1)
            
            # Key text
            key_text = self.font_medium.render(display_key, True, WHITE)
            key_rect = key_text.get_rect(center=button_rect.center)
            self.screen.blit(key_text, key_rect)
        
        # Back button
        back_rect = pygame.Rect(50, SCREEN_HEIGHT - 100, 100, 50)
        pygame.draw.rect(self.screen, (60, 60, 60), back_rect)
        pygame.draw.rect(self.screen, GRAY, back_rect, 2)
        back_text = self.font_medium.render("Back", True, WHITE)
        back_text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, back_text_rect)
        
        # Reset button
        reset_rect = pygame.Rect(200, SCREEN_HEIGHT - 100, 150, 50)
        pygame.draw.rect(self.screen, (60, 60, 60), reset_rect)
        pygame.draw.rect(self.screen, GRAY, reset_rect, 2)
        reset_text = self.font_medium.render("Reset", True, WHITE)
        reset_text_rect = reset_text.get_rect(center=reset_rect.center)
        self.screen.blit(reset_text, reset_text_rect)