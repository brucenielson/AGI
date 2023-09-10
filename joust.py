import pygame
import random

# Exploring PandasAI
# https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key
# https://platform.openai.com/account/api-keys
# https://medium.com/mlearning-ai/conversations-with-pandas-installing-pandas-ai-ea220d9c4cbb
# https://github.com/gventuri/pandas-ai?utm_source=tldrnewsletter


# Build a full game of the video game Joust
# This is a two player game
# Each player has a bird that can fly around the screen
# Each player can flap their wings to fly up
# Each player can move left and right
# Each player can attack the other player
# Each player can attack the other player's bird
# Each player can attack the other player's egg
# Each player can attack the other player's platform


# Initialize Pygame
pygame.init()

# Set the dimensions of the game window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Set the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Create the game window
game_window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# Set the game title
pygame.display.set_caption('Joust')

# Set the clock
clock = pygame.time.Clock()


# Define the player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 0
        self.speed_y = 0

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0


# Define the enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = random.randint(-5, 5)
        self.speed_y = random.randint(-5, 5)

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.right > WINDOW_WIDTH:
            self.speed_x = -self.speed_x
        if self.rect.left < 0:
            self.speed_x = -self.speed_x
        if self.rect.bottom > WINDOW_HEIGHT:
            self.speed_y = -self.speed_y
        if self.rect.top < 0:
            self.speed_y = -self.speed_y


# Create the player and enemy sprites
all_sprites = pygame.sprite.Group()
player = Player(200, 200)
enemy = Enemy(400, 400)
all_sprites.add(player, enemy)

# Define the main game loop
running = True
while running:

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.speed_x = -5
            if event.key == pygame.K_RIGHT:
                player.speed_x = 5
            if event.key == pygame.K_UP:
                player.speed_y = -5
            if event.key == pygame.K_DOWN:
                player.speed_y = 5
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT and player.speed_x < 0:
                player.speed_x = 0
            if event.key == pygame.K_RIGHT and player.speed_x > 0:
                player.speed_x = 0
            if event.key == pygame.K_UP and player.speed_y < 0:
                player.speed_y = 0

# Update sprites
all_sprites.update()

# Check for collisions between the player and enemy
if pygame.sprite.collide_rect(player, enemy):
    running = False

# Draw the game window
game_window.fill(BLACK)
all_sprites.draw(game_window)
pygame.display.flip()

# Set the frame rate
clock.tick(60)
