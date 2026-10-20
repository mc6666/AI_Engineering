import pygame
import random
import sys
import os

# =========================
# 初始化
# =========================

pygame.init()
pygame.mixer.init()

WIDTH = 1000
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("進階配對記憶力遊戲")

clock = pygame.time.Clock()

# =========================
# 音樂
# =========================

pygame.mixer.music.load("assets/bgm.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# =========================
# 顏色
# =========================

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
BLUE = (70, 130, 180)
GREEN = (100, 220, 100)
RED = (220, 80, 80)

# =========================
# 字型
# =========================

font = pygame.font.SysFont("arial", 36)
small_font = pygame.font.SysFont("arial", 28)

# =========================
# 卡片設定
# =========================

ROWS = 4
COLS = 4

CARD_WIDTH = 140
CARD_HEIGHT = 140

MARGIN = 20

start_x = 150
start_y = 120

# =========================
# 載入圖片
# =========================

front_images = []

for i in range(1, 9):

    img = pygame.image.load(f"assets/img{i}.png")
    img = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))

    front_images.append(img)

back_image = pygame.image.load("assets/back.png")
back_image = pygame.transform.scale(
    back_image,
    (CARD_WIDTH, CARD_HEIGHT)
)

# 建立配對
card_images = front_images * 2
random.shuffle(card_images)

# =========================
# 卡片資料
# =========================

revealed = [True] * 16
matched = [False] * 16

flip_scale = [1.0] * 16

first_card = None
second_card = None

lock = False

moves = 0

preview_done = False

start_time = pygame.time.get_ticks()

# =========================
# 卡片位置
# =========================

card_rects = []

for row in range(ROWS):

    for col in range(COLS):

        x = start_x + col * (CARD_WIDTH + MARGIN)
        y = start_y + row * (CARD_HEIGHT + MARGIN)

        rect = pygame.Rect(
            x,
            y,
            CARD_WIDTH,
            CARD_HEIGHT
        )

        card_rects.append(rect)

# =========================
# Reset 按鈕
# =========================

reset_button = pygame.Rect(820, 40, 140, 50)

# =========================
# 重置遊戲
# =========================

def reset_game():

    global revealed
    global matched
    global first_card
    global second_card
    global lock
    global moves
    global preview_done
    global start_time
    global card_images

    card_images = front_images * 2
    random.shuffle(card_images)

    revealed = [True] * 16
    matched = [False] * 16

    first_card = None
    second_card = None

    lock = False

    moves = 0

    preview_done = False

    start_time = pygame.time.get_ticks()

# =========================
# 畫面
# =========================

def draw():

    screen.fill((240, 240, 255))

    # 標題
    title = font.render(
        "Memory Matching Game",
        True,
        BLACK
    )

    screen.blit(title, (320, 30))

    # 步數
    move_text = small_font.render(
        f"Moves: {moves}",
        True,
        BLACK
    )

    screen.blit(move_text, (50, 40))

    # Reset Button
    pygame.draw.rect(screen, RED, reset_button)

    btn_text = small_font.render(
        "RESET",
        True,
        WHITE
    )

    screen.blit(btn_text, (850, 50))

    # 卡片
    for i, rect in enumerate(card_rects):

        scale = flip_scale[i]

        scaled_width = int(CARD_WIDTH * scale)

        img_x = rect.x + (CARD_WIDTH - scaled_width) // 2

        if revealed[i] or matched[i]:

            image = pygame.transform.scale(
                card_images[i],
                (scaled_width, CARD_HEIGHT)
            )

        else:

            image = pygame.transform.scale(
                back_image,
                (scaled_width, CARD_HEIGHT)
            )

        screen.blit(image, (img_x, rect.y))

        pygame.draw.rect(screen, BLACK, rect, 2)

    # 完成訊息
    if all(matched):

        win_text = font.render(
            f"YOU WIN! Moves: {moves}",
            True,
            GREEN
        )

        screen.blit(win_text, (300, 750))

    pygame.display.flip()

# =========================
# 翻牌動畫
# =========================

def animate_flip(index, reveal=True):

    for scale in range(100, 0, -10):

        flip_scale[index] = scale / 100

        draw()
        pygame.time.delay(15)

    revealed[index] = reveal

    for scale in range(0, 101, 10):

        flip_scale[index] = scale / 100

        draw()
        pygame.time.delay(15)

# =========================
# 配對檢查
# =========================

def check_match():

    global first_card
    global second_card
    global lock
    global moves

    moves += 1

    if card_images[first_card] == card_images[second_card]:

        matched[first_card] = True
        matched[second_card] = True

    else:

        pygame.time.delay(700)

        animate_flip(first_card, False)
        animate_flip(second_card, False)

    first_card = None
    second_card = None

    lock = False

# =========================
# 主迴圈
# =========================

running = True

while running:

    clock.tick(60)

    current_time = pygame.time.get_ticks()

    # 開場預覽
    if not preview_done and current_time - start_time > 5000:

        for i in range(16):

            animate_flip(i, False)

        preview_done = True

    # =====================
    # Event
    # =====================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_pos = event.pos

            # Reset
            if reset_button.collidepoint(mouse_pos):

                reset_game()

            if lock or not preview_done:
                continue

            for i, rect in enumerate(card_rects):

                if rect.collidepoint(mouse_pos):

                    if revealed[i] or matched[i]:
                        continue

                    animate_flip(i, True)

                    # 第一張
                    if first_card is None:

                        first_card = i

                    # 第二張
                    elif second_card is None:

                        second_card = i

                        lock = True

                        check_match()

    draw()

pygame.quit()
sys.exit()