import subprocess
from config import *
from load_questions import get_questions

class Fighter(pygame.sprite.Sprite):
    def __init__(self, name ,image, animation_list, x, y, max_hp, damage, group):
        super().__init__(group)
        self.image = image
        self.rect = image.get_rect(topleft=(x, y))

        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.damage = damage
        self.alive = True

        self.animation_list = animation_list
        self.frame_index = 0
        self.action = 0 # 0 = idle, 2 = attack ,1 = hurt
        self.update_time = pygame.time.get_ticks()

    def update(self, animation_type):
        cooldown = 150 if self.action > 0 else 350
        current_time = pygame.time.get_ticks()

        self.image = self.animation_list[self.action][self.frame_index]
        if current_time - self.update_time >= cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            self.update_time = pygame.time.get_ticks()
            self.frame_index = 0
            self.action = 0

    def draw_health_bar(self, x, y):
        ratio = self.hp / self.max_hp

        pygame.draw.rect(screen, 'red', (x, y, 300, 40))
        pygame.draw.rect(screen, 'green', (x, y, 300 * ratio, 40))

        # name
        text = name_font.render(self.name, True, 'black')
        text_rect = text.get_rect(topleft=(x + 10, y + 10))
        screen.blit(text, text_rect)

    def attack(self, target, result):
        bonus_damage = random.randint(5, 20) if result else 0
        damage = self.damage + bonus_damage
        target.hp -= damage

        # check if enemy death
        if target.hp < 1:
            target.hp = 0
            target.alive = False

        damage_text = DamageText(target.rect.centerx, target.rect.centery, str(damage), "red")
        damage_text_group.add(damage_text)

        #animate player attack
        self.action = 2
        self.frame_index = 0

    def hurt(self):
        self.action = 1
        self.frame_index = 0

    def death(self, text):
        self.alive = False
        surf = pygame.Surface((500, 150))
        rect = surf.get_rect(center=(screen_width // 2, screen_height // 2))
        pygame.draw.rect(screen, 'white', rect)

        font = pygame.font.Font(None, (32*5))
        text = font.render(text, True, 'black').convert_alpha()
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, colour):
        pygame.sprite.Sprite.__init__(self)
        font = pygame.font.Font(None, 30)
        self.image = font.render(f'- {damage}', True, colour)
        self.rect = self.image.get_rect(center=(x, y))
        self.counter = 0

    def update(self):
        self.rect.y -= 1.5
        self.counter += 1
        if self.counter >= 40:
            self.kill()

class ActionButton(pygame.sprite.Sprite):
    def __init__(self, image, size, position, color, group):
        pygame.sprite.Sprite.__init__(self, group)
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill(color)
        surf.blit(image, (0, 0))

        self.image = surf
        self.rect = self.image.get_rect(center=position)
        self.color = color

    def draw(self):
        screen.blit(self.image, self.rect)


def get_image(sheet, left, top, size, color):
    sheet = pygame.image.load(f'assets/entity/{sheet}.png').convert_alpha()
    surf = pygame.Surface((32, 32)).convert_alpha()
    surf.blit(sheet, (0, 0), (left, top, 32, 32))
    surf = pygame.transform.scale(surf, size)
    surf.set_colorkey(color)
    return surf

def get_random_question(questions):
    question = random.choice(questions)  # Pick a question from the topic

    correct_answer = question['answer']

    # Get other incorrect answersc
    all_answers = [q['answer'] for q in questions]
    incorrect_answers = random.sample([a for a in all_answers if a != correct_answer], 3)

    # Shuffle options
    options = [correct_answer] + incorrect_answers
    random.shuffle(options)

    return question['question'], correct_answer, options

def draw_questions(question):
    # Render the question
    font = pygame.font.Font(None, 36)
    question_text = font.render(question, True, 'white')
    question_rect = question_text.get_rect(center=(screen_width // 2, screen_height - action_interface + 50))
    x = screen_width // 2 - 200
    y = screen_height - action_interface + 15
    rect = pygame.Rect(x, y, 400, 80)
    pygame.draw.rect(screen, 'black', rect)
    screen.blit(question_text, question_rect)

    # Render the options
    for i, option in enumerate(options):
        x = 20 if i < 2 else screen_width - 400 - 20
        y = screen_height - action_interface + (80 * (i % 2) + 100)
        rect = pygame.Rect(x, y, 400, 80)
        pygame.draw.rect(screen, 'blue', rect)
        pygame.draw.rect(screen, 'black', rect, 5)

        option_text = font.render(option, True, 'white')
        option_rect = option_text.get_rect(center=rect.center)
        screen.blit(option_text, option_rect)

def draw_window(choose):
    screen.blit(bg, (0, 0))
    screen.blit(action_bg, (0, screen_height - action_interface))

    fighter_group.update(player_animation[player.action])
    fighter_group.draw(screen)

    player.draw_health_bar(0, 0)
    enemy.draw_health_bar(screen_width - 300, 0)

    if choose:
        action_button_group.update()
        action_button_group.draw(screen)
    else:
        draw_questions(asked_question)

    damage_text_group.update()
    damage_text_group.draw(screen)

    if not enemy.alive:
        enemy.death("You Win")
    elif not player.alive:
        player.death("You lose")

    pygame.display.flip()

damage_text_group = pygame.sprite.Group()

# Screen setup
action_interface = 300
screen_width = 1200
screen_height = 600 + action_interface
action_interface_center = screen_height - (action_interface // 2)
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Dungeon Game')

# import font
name_font = pygame.font.Font(None, 32)

# import question
topics = get_questions(0)

# Load background
bg = pygame.transform.scale(
    pygame.image.load('assets/background/dungeon_background.jpg'),
    (screen_width, screen_height - action_interface)
).convert_alpha()
action_bg = pygame.transform.scale(
    pygame.image.load('assets/background/action.jpg'),
    (screen_width, action_interface)
).convert_alpha()

# import icon
action_button_group = pygame.sprite.Group()
staff_image = pygame.transform.scale(pygame.image.load('assets/icon/staff.png'), (150, 150))
heal_potion_image = pygame.transform.scale(pygame.image.load('assets/icon/heal_potion.png'), (150, 150))
forfeit_image = pygame.transform.scale(pygame.image.load('assets/icon/run.png'), (150, 150))

staff = ActionButton(staff_image, staff_image.get_size(), (100, action_interface_center), 'red', action_button_group)
heal_potion = ActionButton(heal_potion_image, heal_potion_image.get_size(), (300, action_interface_center), 'green', action_button_group)
forfeit = ActionButton(forfeit_image, forfeit_image.get_size(), (screen_width - forfeit_image.get_width() - 100, action_interface_center), 'blue', action_button_group)


# load player and enemy image
player_image = get_image('spritesheet_1', 0, 0, (320, 320), (255, 255, 255))
player_animation = [
    [get_image('spritesheet_1', (32 * x), 0, (320, 320), (255, 255, 255)) for x in range(6)],
    [get_image('Enemy', (32 * 4), 0, (320, 320), (255, 255, 255))],
    [get_image('spritesheet_1', (32 * x), 32, (320, 320), (255, 255, 255)) for x in range(7)]
]
enemy_image = get_image('enemy', 0, 0, (320, 320), '#45bd57')
enemy_animation = [
    [get_image('Enemy', 0, 0, (320, 320), '#45bd57')],
    [get_image('Enemy', 32, 0, (320, 320), '#45bd57')],
    [get_image('spritesheet_1', (32 * x), 32, (320, 320), (255, 255, 255)) for x in range(7)]
]

enemy_image1 = get_image('enemy', 64, 0, (320, 320), '#45bd57')
enemy_animation1 = [
    [get_image('Enemy', 64, 0, (320, 320), '#45bd57')],
    [get_image('Enemy', 96, 0, (320, 320), '#45bd57')],
    [get_image('spritesheet_1', (32 * x), 32, (320, 320), (255, 255, 255)) for x in range(7)]
]

# initialize    Player and enemy
fighter_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
player = Fighter('Player' ,player_image, player_animation, 40, 150, 400, 100, fighter_group)
enemy = Fighter('Enemy',enemy_image, enemy_animation, (screen_width - enemy_image.get_width() - 20), 150, 1000, 80, fighter_group)
enemy1 = Fighter('Enemy',enemy_image1, enemy_animation1, (screen_width - enemy_image.get_width() ), 150, 1000, 80, fighter_group)

# game variable
current_fighter = 1
total_fighter = 2
attack_cooldown = 0
attack_wait_time = 90
attack = False
heal = False
fighting = False
choose_enemy = False
action = 0 # -1 = forfeit, 0 = stay, 1 = heal, 2 = attack

answer_cooldown = 300  # Cooldown in milliseconds
last_answer_time = 0  # Stores the time when the player answered


# handle quiz
topic_index = 2
asked_question, answer, options = get_random_question(topics[topic_index])
choose_answer = False
correct = False


# Main loop
clock = pygame.time.Clock()
running = True
while running:
    clock.tick(60)
    draw_window(choose_answer)

    # fighting sequence
    if fighting:
        # control actions
        attack = False
        target = None
        pos = pygame.mouse.get_pos()

        if current_fighter == 1:
            # if heal
            if action == 1:
                heal_amount = 50 if player.hp + 50 < player.max_hp else player.max_hp - player.hp
                player.hp += heal_amount
                action = 0
                current_fighter += 1
                attack_cooldown = 0

                heal_text = DamageText(player.rect.centerx, player.rect.centery, str(heal_amount), "green")
                damage_text_group.add(heal_text)

            # if attack enemy
            elif action == 2:
                # target the enemy
                if enemy.rect.collidepoint(pos):
                    attack = True
                    target = enemy
                    choose_enemy = False

                # player action
                if player.alive and enemy.alive:
                    attack_cooldown += 1
                    if attack_cooldown >= attack_wait_time:
                        #attack
                        if attack and target is not None:
                            player.attack(target, correct)
                            target.action = 1
                            current_fighter += 1
                            attack_cooldown = 0
                            action = 0


            elif action == -1:
                screen.fill('black')
                font = pygame.font.Font(None, 40)
                loading_text = font.render("Loading...", True, 'white')
                screen.blit(loading_text, (screen_width // 2 - 50, screen_height // 2))
                pygame.display.update()
                pygame.time.delay(2000)

                pygame.quit()
                subprocess.call([sys.executable, 'main.py'])
                exit()

        # enemy action
        if current_fighter > 1:
            if enemy.alive:
                attack_cooldown += 1
                if attack_cooldown >= attack_wait_time:
                    enemy.attack(player, not correct)
                    current_fighter += 1
                    attack_cooldown = 0
            else:
                current_fighter += 1

        # reset turn
        if current_fighter > total_fighter:
            current_fighter = 1
            fighting = False  # Stop fighting after all fighters have attacked
            choose_answer = False  # Force player to answer a new question

    # event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # choose answer
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if not fighting:
                # Check which options is clicked
                for i, option in enumerate(options):
                    rect_x = 20 if i < 2 else screen_width - 400 - 20
                    rect_y = screen_height - action_interface + (80 * (i % 2) + 95)
                    if pygame.Rect(rect_x, rect_y, 400, 80).collidepoint(mouse_x, mouse_y):
                        choose_answer = True
                        correct =  option == answer

                        last_answer_time = pygame.time.get_ticks()

                        # Load a new question
                        asked_question, answer, options = get_random_question(topics[topic_index])
                        fighting = True

            # choose action when fighting
            else:
                # delay after transitioning from quiz to fighting
                current_time = pygame.time.get_ticks()
                if current_time - last_answer_time >= answer_cooldown:
                    if heal_potion.rect.collidepoint(mouse_x, mouse_y):
                        action = 1
                    elif staff.rect.collidepoint(mouse_x, mouse_y):
                        action = 2
                    elif forfeit.rect.collidepoint(mouse_x, mouse_y):
                        action = -1

pygame.quit()
sys.exit()