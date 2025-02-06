from config import *


class Character(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__()
        self.image = image
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=pos)

class ChatBox(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((SCREEN_WIDTH * 0.8, SCREEN_HEIGHT // 4))
        self.rect = self.image.get_rect(topleft=pos)
        self.font = pygame.font.Font(None, 40)
        self.question_text = "How are you"
        self.user_text = ""
        self.user_text_color = 'black'

        self.update()

    def update(self):
        self.image.fill('#bdbdbd')

        question_label = self.font.render('Pronounce this word:', True, 'red')
        font = pygame.font.Font(None, 24)
        info = font.render('(for 20% discount!)', True, 'red')
        self.image.blit(question_label, (20, 20))
        self.image.blit(info, (20, 50))

        question = self.font.render(self.question_text, True, 'black')
        self.image.blit(question, (40, 100))

        if self.user_text:
            user_label = self.font.render('You said:', True, 'navy')
            user_label_rect = user_label.get_rect(topleft=(self.image.get_width() // 2 + 100, 20))
            self.image.blit(user_label, user_label_rect)

            user_response = self.font.render(self.user_text, True, self.user_text_color)
            user_response_rect = user_response.get_rect(topleft=(self.image.get_width() // 2 + 100, 60))
            self.image.blit(user_response, user_response_rect)

        mic = pygame.transform.scale(pygame.image.load('assets/icon/microphone.png'), (100, 100))
        mic_rect = mic.get_rect(center=(self.image.get_width() // 2, self.image.get_height() // 2))
        self.image.blit(mic, mic_rect)

    def write_user_word(self, word, color):
        self.user_text = word
        self.user_text_color = color
        self.update()

def get_image(sheet, left, top, size, color):
    sheet = pygame.image.load(f'assets/entity/{sheet}').convert_alpha()
    surf = pygame.Surface((32, 32)).convert_alpha()
    surf.blit(sheet, (0, 0), (left, top, 32, 32))
    surf = pygame.transform.scale(surf, size)
    surf.set_colorkey(color)
    return surf

def draw_background(situation, result):
    if not situation:
        screen.blit(bg, (0, 0))
        screen.blit(npc.image, npc.rect)
        screen.blit(chat.image, chat.rect)
    else:
        screen.blit(bg, (0, 0))
        for i, rect in enumerate(display_rects):
            pygame.draw.rect(screen, 'chocolate', rect)
            pygame.draw.rect(screen, 'orange', rect, 4)

            potion_place = [rect.centerx - heal_potion.get_width()//2, rect.centery - heal_potion.get_height()//2]
            screen.blit(potions[i], (potion_place[0], potion_place[1]))

            padding = 10
            price = prices[i] * 8 // 10 if result else prices[i]
            price_surf = main_font.render(str(price), True, 'gold')
            price_rect = price_surf.get_rect(bottomleft=(rect.left + padding, rect.bottom - padding))
            screen.blit(price_surf, price_rect)

            coin_rect = coin.get_rect(midleft=(price_rect.right - 20, price_rect.centery))
            screen.blit(coin, coin_rect)

#
main_font = pygame.font.Font(None, 42)

bg = pygame.transform.scale(pygame.image.load('assets/background/shop.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT))

rect_size = [300, 300]
display_rects = [pygame.rect.Rect(50 * (x+1) + rect_size[0] * x, SCREEN_HEIGHT // 2 - rect_size[1] // 2, rect_size[0], rect_size[1]) for x in range(2)]

heal_potion = pygame.transform.scale(pygame.image.load('assets/icon/heal_potion.png'), (200, 200))
poison_potion = pygame.transform.scale(pygame.image.load('assets/icon/poison_potion.jpg'), (200, 200))
coin = pygame.transform.scale(pygame.image.load('assets/icon/coin.png'), (75, 75))

potions = [heal_potion, poison_potion]
prices = [5, 10]

npc_image = get_image('npc.png', 0, 32, (350, 350), 'black')
npc = Character(npc_image, (SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT - 350))

chat = ChatBox((SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.7))

# Track transition time
start_time = None
shopping = False
correct = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_c] and start_time is None:
        chat.write_user_word("How are you", 'green')
        start_time = pygame.time.get_ticks()  # Start timer
        correct = True
    elif keys[pygame.K_w] and start_time is None:
        chat.write_user_word("Hello", 'red')
        start_time = pygame.time.get_ticks()
        correct = False
    elif keys[pygame.K_BACKSPACE]:
        shopping = False
        start_time = None
        chat.write_user_word('', 'black')

    # Delay transition to shopping
    if start_time and pygame.time.get_ticks() - start_time > 1500:
        shopping = True
        start_time = None  # Reset timer after transition

    draw_background(shopping, correct)
    pygame.display.flip()

pygame.quit()
