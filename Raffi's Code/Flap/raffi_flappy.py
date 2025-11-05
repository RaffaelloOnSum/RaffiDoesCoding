#!/usr/bin/env python3
"""
Raffi Flappy — a clean, production-quality Flappy Bird clone using pygame.

Requirements
------------
- Python 3.8+
- pygame (`pip install pygame`)

Run
---
    python raffi_flappy.py

Notes
-----
- No external assets are used; everything is drawn with pygame primitives.
- The bird is named "Raffi" (see window title and code).
- Game features: start screen, gameplay, game over screen, restart, scoring,
  difficulty scaling, smooth physics, 60 FPS.
"""

import math
import random
import sys
from dataclasses import dataclass
from typing import List, Tuple

import pygame

# -------------------------------
# Configuration & Constants
# -------------------------------

WIDTH, HEIGHT = 432, 768        # Classic tall canvas (mobile-like)
FPS = 60

GROUND_H = 96                   # Height of the ground strip
PLAY_AREA_H = HEIGHT - GROUND_H

GRAVITY = 1500.0                # px / s^2
FLAP_IMPULSE = -420.0           # px / s (instantaneous velocity set when flapping)
MAX_FALL_SPEED = 900.0

PIPE_SPEED_BASE = 180.0         # px / s (will scale up)
PIPE_SPAWN_INTERVAL = 1.35      # seconds between spawns (will scale down)
PIPE_GAP_BASE = 210             # base gap (will scale down)
PIPE_WIDTH = 78

DIFFICULTY_TIME_TO_MAX = 90.0   # seconds to reach near max difficulty

BIRD_X = WIDTH // 4
BIRD_RADIUS = 18

# Colors
SKY = (135, 206, 235)
GROUND = (224, 200, 145)
PIPE_GREEN = (0, 160, 75)
PIPE_DARK = (0, 120, 60)
WHITE = (250, 250, 250)
BLACK = (20, 20, 20)
YELLOW = (255, 220, 85)
ORANGE = (255, 170, 50)
RED = (220, 50, 60)
SHADOW = (0, 0, 0, 64)


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def ease_out_quint(t: float) -> float:
    """Ease function used for start screen animation."""
    return 1 - pow(1 - t, 5)


def circle_rect_collision(cx: float, cy: float, cr: float, rx: float, ry: float, rw: float, rh: float) -> bool:
    """
    Accurate circle-rectangle collision.
    (cx, cy) circle center; radius cr.
    Rect at (rx, ry) with size (rw, rh).
    """
    # Find the closest point on the rectangle to the circle center
    closest_x = clamp(cx, rx, rx + rw)
    closest_y = clamp(cy, ry, ry + rh)
    dx = cx - closest_x
    dy = cy - closest_y
    return (dx * dx + dy * dy) <= (cr * cr)


@dataclass
class PipePair:
    """
    Represents a pair of pipes (top & bottom) with a vertical gap.
    x: left position
    gap_y: vertical center of the gap
    gap_h: gap height
    """
    x: float
    gap_y: float
    gap_h: float
    width: int = PIPE_WIDTH
    passed: bool = False  # Whether bird has scored for this pair

    @property
    def rects(self) -> Tuple[pygame.Rect, pygame.Rect]:
        top_h = max(0, int(self.gap_y - self.gap_h / 2))
        bot_y = int(self.gap_y + self.gap_h / 2)
        bot_h = max(0, PLAY_AREA_H - bot_y)
        top = pygame.Rect(int(self.x), 0, self.width, top_h)
        bottom = pygame.Rect(int(self.x), bot_y, self.width, bot_h)
        return top, bottom

    def update(self, dt: float, speed: float) -> None:
        self.x -= speed * dt

    def is_offscreen(self) -> bool:
        return self.x + self.width < 0

    def draw(self, surf: pygame.Surface) -> None:
        top, bottom = self.rects
        # Draw pipes with a lip for a nicer look
        for r in (top, bottom):
            pygame.draw.rect(surf, PIPE_GREEN, r)
            lip = pygame.Rect(r.left - 6, r.top, r.width + 12, 20)
            if r.top > 0:  # bottom pipe
                lip.top = r.top
            else:          # top pipe: draw lip at bottom end
                lip.top = r.bottom - 20
            pygame.draw.rect(surf, PIPE_DARK, lip)


class Bird:
    """The player-controlled bird 'Raffi' with smooth physics and a simple wing animation."""

    def __init__(self, x: int, y: int, radius: int) -> None:
        self.x = float(x)
        self.y = float(y)
        self.r = radius
        self.vy = 0.0
        self.alive = True
        self.wing_phase = 0.0    # 0..1 loop for wing flapping animation
        self.rot = 0.0           # visual rotation for tilt

    def reset(self, y: int) -> None:
        self.y = float(y)
        self.vy = 0.0
        self.alive = True
        self.wing_phase = 0.0
        self.rot = 0.0

    def flap(self) -> None:
        """Instant upward velocity; clamp to avoid stacking too high."""
        self.vy = FLAP_IMPULSE

    def update(self, dt: float) -> None:
        if not self.alive:
            # Bird falls even after death
            self.vy = clamp(self.vy + GRAVITY * dt, -9999, MAX_FALL_SPEED)
            self.y += self.vy * dt
            self.rot = clamp(self.rot + 240 * dt, -30, 70)
            self.wing_phase = (self.wing_phase + 2.0 * dt) % 1.0
            return

        # Alive physics
        self.vy = clamp(self.vy + GRAVITY * dt, -9999, MAX_FALL_SPEED)
        self.y += self.vy * dt

        # Visual rotation based on vertical speed
        target_rot = clamp(self.vy * 0.10, -35, 70)
        # Smooth rotate
        self.rot += (target_rot - self.rot) * clamp(dt * 8.0, 0.0, 1.0)

        # Wing flapping speed varies with vertical motion
        flap_speed = 4.0 if self.vy < -50 else 2.6
        self.wing_phase = (self.wing_phase + flap_speed * dt) % 1.0

    @property
    def pos(self) -> Tuple[int, int]:
        return int(self.x), int(self.y)

    def circle(self) -> Tuple[float, float, float]:
        return self.x, self.y, self.r

    def collides_with_rect(self, rect: pygame.Rect) -> bool:
        cx, cy, cr = self.circle()
        return circle_rect_collision(cx, cy, cr, rect.left, rect.top, rect.width, rect.height)

    def draw(self, surf: pygame.Surface) -> None:
        # Shadow for depth
        shadow_y = self.y + 4
        pygame.draw.circle(surf, (0, 0, 0), (int(self.x + 2), int(shadow_y)), self.r)

        # Body (gradient-ish with two tones)
        pygame.draw.circle(surf, ORANGE, self.pos, self.r)
        pygame.draw.circle(surf, YELLOW, (self.pos[0] - 4, self.pos[1] - 4), int(self.r * 0.78))

        # Eye
        eye_r = max(2, int(self.r * 0.15))
        eye_x = int(self.x + self.r * 0.3)
        eye_y = int(self.y - self.r * 0.2)
        pygame.draw.circle(surf, WHITE, (eye_x, eye_y), eye_r + 1)
        pygame.draw.circle(surf, BLACK, (eye_x, eye_y), eye_r)

        # Beak (triangle)
        beak_len = int(self.r * 0.9)
        beak_h = int(self.r * 0.5)
        angle_rad = math.radians(self.rot)
        # Beak points to the right; tilt with rotation
        tip = (int(self.x + math.cos(angle_rad) * (self.r + beak_len)),
               int(self.y + math.sin(angle_rad) * (self.r + beak_len)))
        base1 = (int(self.x + math.cos(angle_rad + math.pi / 2) * beak_h),
                 int(self.y + math.sin(angle_rad + math.pi / 2) * beak_h))
        base2 = (int(self.x + math.cos(angle_rad - math.pi / 2) * beak_h),
                 int(self.y + math.sin(angle_rad - math.pi / 2) * beak_h))
        pygame.draw.polygon(surf, (255, 150, 0), [base1, base2, tip])

        # Wing (ellipse) with simple flap animation: phase 0..1 maps to offset
        flap = math.sin(self.wing_phase * 2 * math.pi)  # -1..1
        wing_offset_y = int(-flap * self.r * 0.45)
        wing_rect = pygame.Rect(0, 0, int(self.r * 1.2), int(self.r * 0.7))
        wing_rect.center = (int(self.x - self.r * 0.5), int(self.y + wing_offset_y))
        pygame.draw.ellipse(surf, ORANGE, wing_rect)


class Game:
    """Main game class orchestrating states, input, updates, drawing, and difficulty scaling."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Raffi — Flappy Bird")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont("arialrounded", 48)
        self.font = pygame.font.SysFont("arialrounded", 28)
        self.font_small = pygame.font.SysFont("arialrounded", 20)

        # Game state
        self.reset_all()

    # --------------- State Management ---------------

    def reset_all(self) -> None:
        self.state = "start"           # start, play, gameover
        self.time = 0.0
        self.score = 0
        self.best_score = 0
        self.bird = Bird(BIRD_X, HEIGHT // 2, BIRD_RADIUS)
        self.pipes: List[PipePair] = []
        self.spawn_t = 0.0             # time since last spawn
        self.scroll_x = 0.0            # for ground parallax

        # Difficulty timers
        self.elapsed_run_time = 0.0    # time spent alive in current run

    def start_run(self) -> None:
        self.state = "play"
        self.score = 0
        self.bird.reset(HEIGHT // 2)
        self.pipes.clear()
        self.spawn_t = 0.0
        self.elapsed_run_time = 0.0

    def end_run(self) -> None:
        self.state = "gameover"
        self.bird.alive = False
        self.best_score = max(self.best_score, self.score)

    # --------------- Difficulty Model ---------------

    def difficulty_factor(self) -> float:
        """0.0 at start of a run, approaching 1.0 by DIFFICULTY_TIME_TO_MAX seconds."""
        t = clamp(self.elapsed_run_time / DIFFICULTY_TIME_TO_MAX, 0.0, 1.0)
        return ease_out_quint(t)

    def current_pipe_speed(self) -> float:
        # Scale speed up to +80% over time
        return PIPE_SPEED_BASE * (1.0 + 0.8 * self.difficulty_factor())

    def current_gap_height(self) -> float:
        # Shrink gap down to 65% of base
        return PIPE_GAP_BASE * (1.0 - 0.35 * self.difficulty_factor())

    def current_spawn_interval(self) -> float:
        # Decrease spawn interval down to 75% base
        return PIPE_SPAWN_INTERVAL * (1.0 - 0.25 * self.difficulty_factor())

    # --------------- Core Loop ---------------

    def run(self) -> None:
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.time += dt
            self.handle_events()
            self.update(dt)
            self.draw()

    # --------------- Event Handling ---------------

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE,):
                    pygame.quit()
                    sys.exit()

                if self.state == "start":
                    if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                        self.start_run()
                        self.bird.flap()
                elif self.state == "play":
                    if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                        self.bird.flap()
                elif self.state == "gameover":
                    if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w, pygame.K_r):
                        self.start_run()
                        self.bird.flap()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == "start":
                    self.start_run()
                    self.bird.flap()
                elif self.state == "play":
                    self.bird.flap()
                elif self.state == "gameover":
                    self.start_run()
                    self.bird.flap()

    # --------------- Update ---------------

    def update(self, dt: float) -> None:
        if self.state == "start":
            # gentle bobbing animation
            self.bird.y = HEIGHT // 2 + math.sin(self.time * 2.2) * 12
            self.bird.wing_phase = (self.bird.wing_phase + 1.8 * dt) % 1.0
            self.scroll_x = (self.scroll_x + self.current_pipe_speed() * 0.4 * dt) % WIDTH
            return

        if self.state == "play":
            self.elapsed_run_time += dt
            self.bird.update(dt)
            speed = self.current_pipe_speed()

            # Spawn pipes
            self.spawn_t += dt
            if self.spawn_t >= self.current_spawn_interval():
                self.spawn_t = 0.0
                gap_h = self.current_gap_height()
                margin = 60
                gap_center = random.uniform(margin + gap_h / 2, PLAY_AREA_H - margin - gap_h / 2)
                self.pipes.append(PipePair(WIDTH + 20, gap_center, gap_h))

            # Update pipes
            for p in self.pipes:
                p.update(dt, speed)

            # Remove offscreen
            self.pipes = [p for p in self.pipes if not p.is_offscreen()]

            # Scoring & collision
            bird_cx, bird_cy, bird_r = self.bird.circle()
            for p in self.pipes:
                top, bot = p.rects

                # Score when center of pipe passes bird
                if not p.passed and p.x + p.width < self.bird.x:
                    p.passed = True
                    self.score += 1

                # Collision with pipes
                if self.bird.collides_with_rect(top) or self.bird.collides_with_rect(bot):
                    self.end_run()

            # Collision with boundaries (ceiling/ground)
            if bird_cy - bird_r <= 0:
                self.end_run()
            if bird_cy + bird_r >= PLAY_AREA_H:
                self.end_run()

            self.scroll_x = (self.scroll_x + speed * dt) % WIDTH

        elif self.state == "gameover":
            # let bird keep falling
            self.bird.update(dt)
            self.scroll_x = (self.scroll_x + self.current_pipe_speed() * 0.4 * dt) % WIDTH

    # --------------- Draw Helpers ---------------

    def draw_background(self) -> None:
        self.screen.fill(SKY)

    def draw_ground(self) -> None:
        # Simple parallax ground with repeating rectangles
        ground_y = PLAY_AREA_H
        pygame.draw.rect(self.screen, GROUND, (0, ground_y, WIDTH, GROUND_H))

        tile_w = 36
        for i in range(-1, WIDTH // tile_w + 2):
            x = int(i * tile_w - (self.scroll_x % tile_w))
            h = 18 if i % 2 == 0 else 10
            pygame.draw.rect(self.screen, (210, 190, 135), (x, ground_y, tile_w, h))

    def draw_score(self, center: bool = False) -> None:
        txt = self.font_big.render(str(self.score), True, WHITE)
        if center:
            rect = txt.get_rect(center=(WIDTH // 2, 100))
        else:
            rect = txt.get_rect(midtop=(WIDTH // 2, 32))
        # Shadow
        shadow = self.font_big.render(str(self.score), True, BLACK)
        shadow_rect = shadow.get_rect(center=rect.center)
        shadow_rect.move_ip(2, 2)
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(txt, rect)

    def draw_start_screen(self) -> None:
        # Title with gentle rise animation
        t = clamp((math.sin(self.time * 1.2) + 1) / 2, 0, 1)
        ease = ease_out_quint(t)
        title = self.font_big.render("Raffi — Flappy Bird", True, WHITE)
        rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 4 - int(12 * (ease - 0.5))))
        # Shadow
        shadow = self.font_big.render("Raffi — Flappy Bird", True, BLACK)
        shadow_rect = shadow.get_rect(center=rect.center)
        shadow_rect.move_ip(3, 3)
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(title, rect)

        prompt = self.font.render("Press SPACE / Click to start", True, WHITE)
        p_rect = prompt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
        self.screen.blit(prompt, p_rect)

        hint = self.font_small.render("Flap: Space • Click • W/Up", True, WHITE)
        h_rect = hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
        self.screen.blit(hint, h_rect)

    def draw_gameover_screen(self) -> None:
        over = self.font_big.render("Game Over", True, WHITE)
        o_rect = over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        shadow = self.font_big.render("Game Over", True, BLACK)
        s_rect = shadow.get_rect(center=o_rect.center)
        s_rect.move_ip(3, 3)
        self.screen.blit(shadow, s_rect)
        self.screen.blit(over, o_rect)

        score_txt = self.font.render(f"Score: {self.score}   Best: {self.best_score}", True, WHITE)
        st_rect = score_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        self.screen.blit(score_txt, st_rect)

        prompt = self.font_small.render("Press SPACE / R to retry", True, WHITE)
        p_rect = prompt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 48))
        self.screen.blit(prompt, p_rect)

    # --------------- Draw ---------------

    def draw(self) -> None:
        self.draw_background()

        # Pipes
        for p in self.pipes:
            p.draw(self.screen)

        # Bird
        self.bird.draw(self.screen)

        # Ground on top
        self.draw_ground()

        # UI
        if self.state == "start":
            self.draw_start_screen()
        elif self.state == "play":
            self.draw_score(center=False)
        elif self.state == "gameover":
            self.draw_score(center=False)
            self.draw_gameover_screen()

        pygame.display.flip()


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
