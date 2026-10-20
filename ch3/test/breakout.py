# -*- coding: utf-8 -*-
"""A small, self-contained Breakout game made with PyGame.

Run with: python breakout.py
"""

import math
import random
import sys

import pygame


WIDTH, HEIGHT = 900, 650
FPS = 60
TOP_BAR = 68
PADDLE_W, PADDLE_H = 118, 16
BALL_RADIUS = 9

BG = (11, 16, 35)
PANEL = (18, 25, 52)
TEXT = (235, 242, 255)
MUTED = (151, 166, 204)
ACCENT = (94, 234, 212)
BRICK_COLORS = [(255, 107, 129), (255, 180, 84), (255, 226, 103), (111, 224, 169), (99, 181, 255)]


def make_bricks(level):
    rows = min(5 + level, 8)
    cols = 10
    gap = 7
    margin = 42
    brick_w = (WIDTH - margin * 2 - gap * (cols - 1)) // cols
    brick_h = 24
    bricks = []
    for row in range(rows):
        for col in range(cols):
            rect = pygame.Rect(
                margin + col * (brick_w + gap),
                TOP_BAR + 34 + row * (brick_h + gap),
                brick_w,
                brick_h,
            )
            bricks.append({"rect": rect, "hits": 1 + (row // 3), "color": BRICK_COLORS[row % len(BRICK_COLORS)]})
    return bricks


def reset_ball(paddle, level):
    speed = 360 + level * 25
    angle = random.choice((-1, 1)) * random.uniform(math.radians(55), math.radians(125))
    return pygame.Vector2(paddle.centerx, paddle.top - BALL_RADIUS - 3), pygame.Vector2(
        math.cos(angle) * speed, -abs(math.sin(angle) * speed)
    )


def draw_text(surface, font, value, pos, color=TEXT, center=False):
    image = font.render(str(value), True, color)
    rect = image.get_rect(center=pos) if center else image.get_rect(topleft=pos)
    surface.blit(image, rect)


def load_font(size):
    """載入支援繁體／簡體中文的字型，避免中文變成方框或亂碼。"""
    font_path = pygame.font.match_font([
        "microsoftjhenghei", "microsoftyahei",
        "noto sans cjk tc", "noto sans cjk sc",
        "simhei", "arial unicode ms",
    ])
    return pygame.font.Font(font_path, size) if font_path else pygame.font.Font(None, size)

def main():
    pygame.init()
    pygame.display.set_caption("Neon Breakout")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    title_font = load_font(30)
    ui_font = load_font(24)
    big_font = load_font(66)
    small_font = load_font(20)

    paddle = pygame.Rect(WIDTH // 2 - PADDLE_W // 2, HEIGHT - 52, PADDLE_W, PADDLE_H)
    level, score, lives = 1, 0, 3
    bricks = make_bricks(level)
    ball, velocity = reset_ball(paddle, level)
    launched = False
    paused = False
    game_over = False
    won = False
    particles = []

    def start_level():
        nonlocal bricks, ball, velocity, launched
        bricks = make_bricks(level)
        ball, velocity = reset_ball(paddle, level)
        launched = False

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.03)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE and not game_over and not won:
                    if paused:
                        paused = False
                    else:
                        launched = True
                elif event.key == pygame.K_p and not game_over and not won:
                    paused = not paused
                elif event.key == pygame.K_r and (game_over or won):
                    level, score, lives = 1, 0, 3
                    paddle.centerx = WIDTH // 2
                    game_over = won = paused = False
                    start_level()

        keys = pygame.key.get_pressed()
        if not paused and not game_over and not won:
            direction = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
            paddle.x += int(direction * 560 * dt)
            paddle.clamp_ip(screen.get_rect().inflate(-18, 0))

            if not launched:
                ball.x = paddle.centerx
                ball.y = paddle.top - BALL_RADIUS - 3
            else:
                old = ball.copy()
                ball += velocity * dt
                if ball.x - BALL_RADIUS <= 0 or ball.x + BALL_RADIUS >= WIDTH:
                    velocity.x *= -1
                    ball.x = max(BALL_RADIUS, min(WIDTH - BALL_RADIUS, ball.x))
                if ball.y - BALL_RADIUS <= TOP_BAR:
                    velocity.y *= -1
                    ball.y = TOP_BAR + BALL_RADIUS
                if velocity.y > 0 and paddle.collidepoint(ball.x, ball.y + BALL_RADIUS):
                    offset = (ball.x - paddle.centerx) / (paddle.width / 2)
                    velocity.x = offset * 450
                    velocity.y = -math.sqrt(max(150, velocity.length_squared() - velocity.x ** 2))
                    ball.y = paddle.top - BALL_RADIUS - 1

                for brick in bricks[:]:
                    rect = brick["rect"]
                    if rect.collidepoint(ball.x, ball.y) or rect.colliderect(pygame.Rect(int(ball.x - BALL_RADIUS), int(ball.y - BALL_RADIUS), BALL_RADIUS * 2, BALL_RADIUS * 2)):
                        brick["hits"] -= 1
                        velocity.y *= -1
                        if brick["hits"] <= 0:
                            bricks.remove(brick)
                            score += 10
                            for _ in range(8):
                                particles.append([pygame.Vector2(rect.center), pygame.Vector2(random.uniform(-90, 90), random.uniform(-100, 30)), 0.45, brick["color"]])
                        else:
                            score += 3
                        break

                if ball.y - BALL_RADIUS > HEIGHT:
                    lives -= 1
                    if lives <= 0:
                        game_over = True
                    else:
                        ball, velocity = reset_ball(paddle, level)
                        launched = False

                if not bricks and not game_over:
                    level += 1
                    if level > 4:
                        won = True
                    else:
                        start_level()

            for particle in particles[:]:
                particle[0] += particle[1] * dt
                particle[2] -= dt
                if particle[2] <= 0:
                    particles.remove(particle)

        screen.fill(BG)
        pygame.draw.rect(screen, PANEL, (0, 0, WIDTH, TOP_BAR))
        pygame.draw.line(screen, (40, 55, 92), (0, TOP_BAR), (WIDTH, TOP_BAR), 2)
        draw_text(screen, title_font, "NEON BREAKOUT", (24, 20), ACCENT)
        draw_text(screen, ui_font, f"SCORE  {score:04d}", (270, 23))
        draw_text(screen, ui_font, f"LEVEL  {level}", (470, 23))
        draw_text(screen, ui_font, f"LIVES  {'●' * lives}{'○' * (3 - lives)}", (660, 23), (255, 180, 84))

        for brick in bricks:
            rect, color = brick["rect"], brick["color"]
            pygame.draw.rect(screen, color, rect, border_radius=6)
            pygame.draw.line(screen, tuple(min(255, c + 40) for c in color), rect.topleft, rect.topright, 2)
            if brick["hits"] > 1:
                pygame.draw.circle(screen, (255, 255, 255), rect.center, 3)

        for pos, _, life, color in particles:
            pygame.draw.circle(screen, (*color, max(0, int(life * 255))), (int(pos.x), int(pos.y)), max(1, int(life * 5)))
        pygame.draw.rect(screen, (36, 218, 204), paddle, border_radius=8)
        pygame.draw.rect(screen, (160, 255, 245), paddle.inflate(-18, -7), border_radius=4)
        pygame.draw.circle(screen, (255, 255, 255), (int(ball.x), int(ball.y)), BALL_RADIUS)
        pygame.draw.circle(screen, ACCENT, (int(ball.x), int(ball.y)), BALL_RADIUS - 3)

        if not launched and not game_over and not won:
            draw_text(screen, small_font, "← → 移動   SPACE 發射   P 暫停", (WIDTH // 2, HEIGHT - 18), MUTED, center=True)
        if paused:
            draw_text(screen, big_font, "PAUSED", (WIDTH // 2, HEIGHT // 2 - 20), TEXT, center=True)
            draw_text(screen, ui_font, "按 SPACE 繼續", (WIDTH // 2, HEIGHT // 2 + 32), MUTED, center=True)
        if game_over or won:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((5, 8, 20, 190))
            screen.blit(overlay, (0, 0))
            draw_text(screen, big_font, "YOU WIN!" if won else "GAME OVER", (WIDTH // 2, HEIGHT // 2 - 35), ACCENT if won else (255, 107, 129), center=True)
            draw_text(screen, ui_font, f"分數 {score}   |   按 R 重新開始", (WIDTH // 2, HEIGHT // 2 + 28), TEXT, center=True)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
