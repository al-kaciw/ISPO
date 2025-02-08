from load_questions import get_questions
from config import *
from suara import SpeechRecognizer

# Screen setup
SCREEN_TITLE = "School"
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)
clock = pygame.time.Clock()
FPS = 60

speech_recognizer = SpeechRecognizer()

# Load Questions
section_index = 0
topics = get_questions(section_index)
questions = topics[0]

# Extract English and Indonesian words
english_words = [q['question'] for q in questions]
indonesian_words = [q['answer'] for q in questions]

# Shuffle Indonesian words while keeping track of their original index
shuffled_indonesian = random.sample(list(enumerate(indonesian_words)), len(indonesian_words))
shuffled_indices, indonesian_words = zip(*shuffled_indonesian)  # Extract shuffled words & indices

# Load Background
background = pygame.transform.scale(pygame.image.load('assets/background/class_background.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT))

# load icon
mic = pygame.transform.scale(pygame.image.load('assets/icon/microphone.png'), (100, 100))

# Font
font = pygame.font.Font(None, 48)

# Sprite Group
sprite_group = pygame.sprite.Group()

class LanguageScroll(pygame.sprite.Sprite):
    def __init__(self, pos, group, words):
        super().__init__(group)
        self.image = pygame.Surface((SCREEN_WIDTH * 0.3, SCREEN_HEIGHT * 0.85))
        self.image.fill('white')
        self.rect = self.image.get_rect(topleft=pos)
        self.selected = None
        self.selected_word_index = None
        self.correct_answer = []
        self.choice_rects = []
        self.choices = words  # Store words list

    def draw_choice(self):
        self.image.fill('white')
        self.choice_rects = []

        amount_choice = len(self.choices)
        rect_height = self.image.get_height() // amount_choice
        for i, choice in enumerate(self.choices):
            text_surface = font.render(choice, True, 'black')

            y = rect_height * i + (rect_height - text_surface.get_height()) // 2
            text_rect = text_surface.get_rect(midtop=(self.image.get_width() // 2, y))

            rect = pygame.Rect(0, rect_height * i, self.image.get_width(), rect_height)
            if i in self.correct_answer:
                box_color = 'green'
            elif self.selected_word_index == i:
                box_color = '#91251d'
            else:
                box_color = '#e03b2f'
            pygame.draw.rect(self.image, box_color, rect)
            pygame.draw.rect(self.image, 'blue', rect, 3)

            self.image.blit(text_surface, text_rect)
            self.choice_rects.append(rect)

    def handle_click(self, mouse_pos):
        local_mouse_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
        for i, rect in enumerate(self.choice_rects):
            if rect.collidepoint(local_mouse_pos):
                self.selected = (self.choices[i], i)  # Store (word, index)
                self.selected_word_index = i
                return self.selected
        return None

class FeedbackScroll(pygame.sprite.Sprite):
    def __init__(self, word, size, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect(topleft=(pos[0] - self.image.get_width() // 2, pos[1] - self.image.get_height() // 2))
        self.explanation_word = word
        self.font = pygame.font.Font(None, 28)

    def wrap_text(self, max_width):
        words = self.explanation_word.split(' ')
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            line_width = font.size(' '.join(current_line))[0]
            if line_width > max_width:
                current_line.pop()  # Remove the last word that caused overflow
                lines.append(' '.join(current_line))
                current_line = [word]  # Start a new line with the word

        if current_line:  # Add any remaining words
            lines.append(' '.join(current_line))

        return lines

    def write_feedback(self):
        max_width = self.image.get_width() - 20  # Leave some padding
        wrapped_lines = self.wrap_text(max_width)

        # Clear the image before drawing text
        self.image.fill('black')

        y_offset = 10  # Starting y position for text
        for line in wrapped_lines:
            text_surface = font.render(line, True, 'white')
            text_rect = text_surface.get_rect(midtop=(self.image.get_width() // 2, y_offset))
            self.image.blit(text_surface, text_rect)
            y_offset += text_surface.get_height() + 5

class Microphone(pygame.sprite.Sprite):
    def __init__(self, image, icon, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.image.fill('white')
        self.rect = self.image.get_rect(midbottom=pos)
        self.image.blit(icon, (0, 0))
        self.feedback_text = ""

    def listen(self, correct_word):
        spoken_text = speech_recognizer.get_speech()
        print(f"Player said: {spoken_text}")

        # Check if pronunciation is correct
        if spoken_text.lower() == correct_word.lower():
            self.feedback_text = "✅ Correct Pronunciation!"
        else:
            self.feedback_text = f"❌ Try Again! You said: {spoken_text}"

    def draw_feedback(self):
        if self.feedback_text:
            text_surface = font.render(self.feedback_text, True, "white")
            text_rect = text_surface.get_rect(midtop=(self.rect.centerx - 50, self.rect.bottom + 10))
            screen.blit(text_surface, text_rect)


def draw_feedback(question_index):
    big = (SCREEN_WIDTH * 6 // 10, SCREEN_HEIGHT * 4 // 10)
    feedback = FeedbackScroll(questions[question_index]['explanation'], big, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    feedback.write_feedback()
    screen.blit(feedback.image, feedback.rect)

    screen.blit(microphone.image, microphone.rect)

def check_matching(selected_englishes, selected_indonesians, index):
    global give_feedback, feedback_index
    english_word, english_index = selected_englishes
    indonesian_word, indonesian_index = selected_indonesians

    # feedback & give color
    if english_index == indonesian_index:
        for scroll in scrolls:
            if scroll == indonesian_scroll:
                scroll.correct_answer.append(index)

            else:
                scroll.correct_answer.append(english_index)

        # draw scroll that give feedback and explanation
        give_feedback = True
        feedback_index = english_index  # Store the correct feedback index

    else:
        print("❌ Incorrect match!")
        for scroll in scrolls:
            scroll.selected_word_index = None
        give_feedback = False  # Prevent feedback from appearing on incorrect answers

def draw_window(mics):
    screen.blit(background, (0, 0))
    english_scroll.draw_choice()
    indonesian_scroll.draw_choice()
    sprite_group.update()
    sprite_group.draw(screen)

    if give_feedback:
        draw_feedback(feedback_index)

    mics.draw_feedback() if mics else None


    pygame.display.flip()


# Create Scrolls for both sides
scroll_width = SCREEN_WIDTH * 0.3
scroll_height = SCREEN_HEIGHT * 0.85
margin_x = scroll_width // 4
margin_y = (SCREEN_HEIGHT - scroll_height) // 2

english_scroll = LanguageScroll((margin_x, margin_y), sprite_group, english_words)
indonesian_scroll = LanguageScroll((SCREEN_WIDTH - margin_x - scroll_width, margin_y), sprite_group,
                                   list(indonesian_words))

scrolls = [english_scroll, indonesian_scroll]

# Main Game Loop
running = True
selected_english = None
selected_indonesian = None
give_feedback = False
feedback_index = None

microphone = Microphone(pygame.Surface((100, 100)), mic, (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.65))


# Inside the game loop
while running:
    screen.fill((0, 0, 0))  # Clear screen

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Quiz section
            if not give_feedback:
                if english_scroll.rect.collidepoint(pygame.mouse.get_pos()):
                    selected_english = english_scroll.handle_click(pygame.mouse.get_pos())

                elif indonesian_scroll.rect.collidepoint(pygame.mouse.get_pos()):
                    selected_indonesian = indonesian_scroll.handle_click(pygame.mouse.get_pos())

                if selected_english and selected_indonesian:
                    indonesian_shuffled_index = selected_indonesian[1]

                    # Convert shuffled index back to original
                    indonesian_original_index = shuffled_indices[selected_indonesian[1]]
                    selected_indonesian = (selected_indonesian[0], indonesian_original_index)

                    check_matching(selected_english, selected_indonesian, indonesian_shuffled_index)

                    selected_english = None
                    selected_indonesian = None

            # Feedback section - Handle mic click
            elif give_feedback and microphone and microphone.rect.collidepoint(pygame.mouse.get_pos()):
                microphone.listen(questions[feedback_index]['question'])  # Check pronunciation

            else:
                give_feedback = False
                microphone.feedback_text = ""

    draw_window(microphone)
    clock.tick(FPS)

pygame.quit()
sys.exit()
