import pygame
import random
import sys
import numpy as np
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Fullscreen setup
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Last Night at Raffi's")

clock = pygame.time.Clock()
font = pygame.font.SysFont("courier", 40, bold=True)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (200, 200, 255)
ENEMY_COLOR = (50, 0, 0)

# Load sounds
try:
    pygame.mixer.music.load("static_drone.wav")
    pygame.mixer.music.play(-1)
except:
    print("Audio file not found, continuing without sound.")

# Creepy messages
messages = [
    "LOCAL 58 BROADCAST INTERRUPTED",
    "AN INTRUDER MAY BE INSIDE",
    "DON'T TRUST YOUR EYES",
    "THERE IS SOMETHING BEHIND YOU"
]

# Player setup
player_size = 30
player_x, player_y = WIDTH//2, HEIGHT//2
player_speed = 6

# Enemy setup
enemy_size = 40
enemy_x = random.randint(0, WIDTH)
enemy_y = random.randint(0, HEIGHT)
enemy_speed = 2

# Flashlight radius
flash_radius = 150

# Jumpscare timer
jumpscare_timer = random.randint(300, 600)

# Heartbeat effect (volume depends on distance)
def heartbeat_volume(player_x, player_y, enemy_x, enemy_y):
    dist = np.hypot(player_x - enemy_x, player_y - enemy_y)
    return max(0.1, min(1.0, 300 / (dist + 1)))

# Draw VHS static
def draw_static():
    noise = np.random.randint(0, 256, (HEIGHT, WIDTH, 3), dtype=np.uint8)
    pygame.surfarray.blit_array(screen, noise.swapaxes(0,1))
    # Add scanlines
    for y in range(0, HEIGHT, 4):
        pygame.draw.line(screen, (0,0,0), (0,y), (WIDTH, y), 1)
    # Add flickering horizontal distort
    if random.random() < 0.05:
        offset = random.randint(-20, 20)
        screen.scroll(dx=offset)

# Flickering text
def draw_text():
    if random.random() < 0.01:
        text = random.choice(messages)
        surf = font.render(text, True, WHITE)
        rect = surf.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(surf, rect)

# Draw player
def draw_player(x, y):
    pygame.draw.rect(screen, PLAYER_COLOR, (x, y, player_size, player_size))

# Draw enemy with flicker/distortion
def draw_enemy(x, y):
    flicker = random.randint(-5,5)
    pygame.draw.rect(screen, ENEMY_COLOR, (x+flicker, y+flicker, enemy_size, enemy_size))

# Flashlight effect with smooth fade
def apply_flashlight(player_x, player_y):
    mask = pygame.Surface((WIDTH, HEIGHT))
    mask.fill(BLACK)
    pygame.draw.circle(mask, (255,255,255), (player_x+player_size//2, player_y+player_size//2), flash_radius)
    mask.set_colorkey((255,255,255))
    mask.set_alpha(220)  # slight transparency for realism
    screen.blit(mask, (0,0))

# Jumpscare flash
def jumpscare():
    face = pygame.Surface((WIDTH, HEIGHT))
    face.fill(WHITE)
    for _ in range(3):
        screen.blit(face, (0,0))
        pygame.display.flip()
        pygame.time.delay(100)
        screen.fill(BLACK)
        pygame.display.flip()
        pygame.time.delay(100)

# Game over screen
def game_over_screen():
    screen.fill(BLACK)
    text = font.render("YOU DIED - PRESS R TO RESTART OR ESC TO QUIT", True, WHITE)
    rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text, rect)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                    main_game()  # Restart game
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

# Main game function
def main_game():
    global player_x, player_y, enemy_x, enemy_y, jumpscare_timer
    player_x, player_y = WIDTH//2, HEIGHT//2
    enemy_x, enemy_y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
    jumpscare_timer = random.randint(300, 600)
    
    running = True
    while running:
        screen.fill(BLACK)
        draw_static()
        draw_text()
        apply_flashlight(player_x, player_y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_size:
            player_x += player_speed
        if keys[pygame.K_UP] and player_y > 0:
            player_y -= player_speed
        if keys[pygame.K_DOWN] and player_y < HEIGHT - player_size:
            player_y += player_speed

        # Enemy movement (smooth chase + erratic flicker)
        if random.random() < 0.05:
            enemy_x += random.randint(-10,10)
            enemy_y += random.randint(-10,10)
        if enemy_x < player_x:
            enemy_x += enemy_speed
        elif enemy_x > player_x:
            enemy_x -= enemy_speed
        if enemy_y < player_y:
            enemy_y += enemy_speed
        elif enemy_y > player_y:
            enemy_y -= enemy_speed

        draw_player(player_x, player_y)
        draw_enemy(enemy_x, enemy_y)

        # Collision check
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        enemy_rect = pygame.Rect(enemy_x, enemy_y, enemy_size, enemy_size)
        if player_rect.colliderect(enemy_rect):
            game_over_screen()

        # Random jumpscare
        jumpscare_timer -= 1
        if jumpscare_timer <= 0:
            jumpscare()
            jumpscare_timer = random.randint(300, 600)

        pygame.display.flip()
        clock.tick(30)

# Start the game
main_game()
