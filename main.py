import pygame
import subprocess
import sys

pygame.init()

# General Setup
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# Colors and Fonts
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
FONT_SIZE = 40
font = pygame.font.Font(None, FONT_SIZE)
TITLE = "Best Game"

# Set up display
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game Menu")

background = pygame.transform.scale(pygame.image.load('assets/background/Map.png'), (SCREEN_WIDTH * 2, SCREEN_HEIGHT * 2))
spritesheets = [pygame.image.load('assets/entity/spritesheet_0.png'),
                pygame.image.load('assets/entity/spritesheet_1.png'),
                pygame.image.load('assets/entity/spritesheet_2.png')]

class Player:
    def __init__(self, img, pos):
        self.image = pygame.transform.scale(img.convert_alpha(), (32, 32))
        self.rect = self.image.get_rect(topleft=pos)
        self.velocity = 5
        self.current_animation = animation_list[0]  # Default to front idle
        self.idle_animation = 0

    def movement(self, keys):
        # Track whether any movement occurred
        moving = False

        # Check for vertical movement
        if keys[pygame.K_DOWN] and self.rect.y + self.rect.height < SCREEN_HEIGHT * 2:
            self.rect.y += self.velocity
            self.current_animation = animation_list[2]  # Front walking
            self.idle_animation = 0  # Front idle
            moving = True
        if keys[pygame.K_UP] and self.rect.y > 0:
            self.rect.y -= self.velocity
            self.current_animation = animation_list[3]  # Back walking
            self.idle_animation = 1  # Back idle
            moving = True

        # Check for horizontal movement
        if keys[pygame.K_LEFT] and self.rect.x > 0:
            self.rect.x -= self.velocity
            self.current_animation = animation_list[7]  # Left walking
            self.idle_animation = 0  # Left idle
            moving = True
        if keys[pygame.K_RIGHT] and self.rect.x + self.rect.width < SCREEN_WIDTH * 2:
            self.rect.x += self.velocity
            self.current_animation = animation_list[6]  # Right walking
            self.idle_animation = 4  # Right idle
            moving = True

        # If no movement occurred, set to idle animation
        if not moving:
            self.current_animation = animation_list[self.idle_animation]


    def update_animation(self):
        self.current_animation.update()
        self.image = self.current_animation.get_current_frame()

class Camera:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface.get_width() // 2
        self.half_h = self.display_surface.get_height() // 2
        self.ground_surface = background
        self.ground_rect = self.ground_surface.get_rect(topleft=(0, 0))

    def center_target_camera(self, target):
        # Calculate potential new offset
        new_offset_x = target.rect.centerx - self.half_w
        new_offset_y = target.rect.centery - self.half_h

        # Clamp the offset to ensure the camera doesn't go beyond the background
        self.offset.x = max(0, min(new_offset_x, self.ground_rect.width - self.display_surface.get_width()))
        self.offset.y = max(0, min(new_offset_y, self.ground_rect.height - self.display_surface.get_height()))

    def custom_draw(self, character):
        # Draw the background with the offset
        ground_offset = self.ground_rect.topleft - self.offset
        self.display_surface.blit(self.ground_surface, ground_offset)

        # Draw the character with the offset
        img_offset = character.rect.topleft - self.offset
        self.display_surface.blit(character.image, img_offset)

camera = Camera()

class Animation:
    def __init__(self, sprite_sheet, frames, animation_type, frame_width, frame_height, scale, color_key, cooldown):
        self.animation = [
            self.get_image(sprite_sheet, x, animation_type, frame_width, frame_height, scale, color_key) for x in range(frames)
        ]
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.cooldown = cooldown

    def get_image(self, sheet, frame, animation_type, width, height, scale, color):
        image = pygame.Surface((width, height)).convert_alpha()
        image.blit(sheet, (0, 0), (width * frame, height * animation_type, width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        image.set_colorkey(color)
        return image

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.cooldown:
            self.current_frame = (self.current_frame + 1) % len(self.animation)
            self.last_update = current_time

    def get_current_frame(self):
        return self.animation[self.current_frame]

animation_list = []
frame_amount = [4, 3, 1]
steps_list = [[6, 6, 6, 6], [6, 7, 6], [6]]
for i in range (3):
    for j in range (frame_amount[i]):
        animation_list.append(Animation(spritesheets[i], steps_list[i][j], j, 32, 32, SCREEN_WIDTH//384, WHITE, 225))

class MenuButton:
    def __init__(self, pos, size, text, background_color, text_color):
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.background_color = background_color
        self.text_color = text_color
        self.text = font.render(text, True, self.text_color)
        self.text_rect = self.text.get_rect(center=self.rect.center)

    def draw_button(self, surface):
        pygame.draw.rect(surface, self.background_color, self.rect)
        surface.blit(self.text, self.text_rect)

start_button = MenuButton((SCREEN_WIDTH // 2 - 100, 150), (200, 50), 'Start', BLACK, WHITE)
setting_button = MenuButton((SCREEN_WIDTH // 2 - 100, 250), (200, 50), 'Setting', BLACK, WHITE)
exit_button = MenuButton((SCREEN_WIDTH - 100, 0), (100, 50), 'Exit', RED, WHITE)

def draw_window(character, animation):
    camera.center_target_camera(character)
    camera.custom_draw(character)
    exit_button.draw_button(window)
    animation.update()
    character.image = animation.get_current_frame()

    pygame.display.update()

def main_menu():
    text_surface = font.render(TITLE, True, BLACK)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
    running = True
    while running:
        window.fill(WHITE)

        window.blit(text_surface, text_rect)
        start_button.draw_button(window)
        setting_button.draw_button(window)
        exit_button.draw_button(window)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.rect.collidepoint(event.pos):
                    return  # Exit menu and start game
                if setting_button.rect.collidepoint(event.pos):
                    print("Settings Button Clicked")
                if exit_button.rect.collidepoint(event.pos):
                    pygame.quit()
                    exit()

def game_loop():
    clock = pygame.time.Clock()
    running = True
    player = Player(animation_list[0].get_current_frame(), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                return  # Return to the main menu
            if event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.rect.collidepoint(event.pos):
                    pygame.quit()
                    exit()

        keys = pygame.key.get_pressed()
        player.movement(keys)  # Update position and animation state
        player.update_animation()  # Update animation frame

        draw_window(player, player.current_animation)

        target_x1, target_y1 = 3160, 740
        target_x2, target_y2 = 1140, 576
        target_x3, target_y3 = 3360, 760
        tolerance = 50  # Allow slight deviation

        if abs(player.rect.centerx - target_x1) <= tolerance and abs(player.rect.centery - target_y1) <= tolerance:
            window.fill(BLACK)
            loading_text = font.render("Loading...", True, WHITE)
            window.blit(loading_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2))
            pygame.display.update()
            pygame.time.delay(2000)

            pygame.quit()
            subprocess.run([sys.executable, 'dungeon.py'])
            exit()

        if abs(player.rect.centerx - target_x2) <= tolerance and abs(player.rect.centery - target_y2) <= tolerance:
            window.fill(BLACK)
            loading_text = font.render("Loading...", True, WHITE)
            window.blit(loading_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2))
            pygame.display.update()
            pygame.time.delay(2000)

            pygame.quit()
            subprocess.run([sys.executable, 'school.py'])
            exit()

        if abs(player.rect.centerx - target_x3) <= tolerance and abs(player.rect.centery - target_y3) <= tolerance:
            window.fill(BLACK)
            loading_text = font.render("Loading...", True, WHITE)
            window.blit(loading_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2))
            pygame.display.update()
            pygame.time.delay(2000)

            pygame.quit()
            subprocess.run([sys.executable, 'potion_store.py'])
            exit()

def main():
    while True:
        main_menu()  # Show the menu
        game_loop()  # Start the game


if __name__ == '__main__':
    main()