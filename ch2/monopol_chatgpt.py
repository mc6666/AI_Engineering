import pygame
import random
import sys

pygame.init()

# ======================
# 基本設定
# ======================
WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Monopoly v2")

FONT = pygame.font.SysFont("arial", 18)
BIG = pygame.font.SysFont("arial", 26)

clock = pygame.time.Clock()

# ======================
# 遊戲參數
# ======================
NUM_TILES = 40
START_MONEY = 1500

players = [
    {"pos": 0, "money": START_MONEY, "name": "P1"},
    {"pos": 0, "money": START_MONEY, "name": "P2"}
]

turn = 0
message = "Player 1 turn - Press R to roll"

# ======================
# 地圖
# ======================
tiles = []
for i in range(NUM_TILES):
    tiles.append({
        "owner": None,
        "price": 100 + (i % 8) * 25,
        "rent": 20 + (i % 5) * 10,
        "type": "chance" if i % 7 == 0 else "property"
    })

# ======================
# 機會卡
# ======================
chance_cards = [
    ("Win $100", 100),
    ("Pay $50", -50),
    ("Go forward 3", "move+3"),
    ("Go back 3", "move-3"),
    ("Bank bonus $200", 200),
]


# ======================
# UI Button
# ======================
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self):
        pygame.draw.rect(screen, (70, 130, 180), self.rect)
        txt = FONT.render(self.text, True, (255, 255, 255))
        screen.blit(txt, (self.rect.x + 10, self.rect.y + 10))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


roll_btn = Button(650, 500, 180, 50, "ROLL DICE")


# ======================
# 核心邏輯
# ======================
def roll_dice():
    return random.randint(1, 6)


def switch_turn():
    global turn, message
    turn = 1 - turn
    message = f"{players[turn]['name']} turn - Press R to roll"


def move_player(steps):
    p = players[turn]
    p["pos"] = (p["pos"] + steps) % NUM_TILES


def chance_event():
    global message

    card = random.choice(chance_cards)
    effect = card[1]

    if isinstance(effect, int):
        players[turn]["money"] += effect
        message = f"Chance: {card[0]}"
    else:
        if effect == "move+3":
            move_player(3)
        elif effect == "move-3":
            move_player(-3)
        message = f"Chance Move: {card[0]}"


def handle_tile():
    global message

    p = players[turn]
    tile = tiles[p["pos"]]

    # chance tile
    if tile["type"] == "chance":
        chance_event()
        return

    # property logic
    if tile["owner"] is None:
        message = f"{p['name']} can buy ${tile['price']} (Press B)"
    elif tile["owner"] != turn:
        p["money"] -= tile["rent"]
        players[tile["owner"]]["money"] += tile["rent"]
        message = f"{p['name']} paid rent ${tile['rent']}"
    else:
        message = "Own property"


def buy_tile():
    p = players[turn]
    tile = tiles[p["pos"]]

    if tile["owner"] is None and p["money"] >= tile["price"]:
        p["money"] -= tile["price"]
        tile["owner"] = turn
        return "Purchased"
    return "Cannot buy"


# ======================
# 繪製棋盤
# ======================
def draw_board():
    cx, cy = 300, 300
    r = 220

    for i in range(NUM_TILES):
        angle = (i / NUM_TILES) * 6.28

        x = cx + int(r * pygame.math.Vector2(1, 0).rotate_rad(angle).x)
        y = cy + int(r * pygame.math.Vector2(1, 0).rotate_rad(angle).y)

        tile = tiles[i]

        color = (200, 200, 200)
        if tile["owner"] == 0:
            color = (100, 200, 100)
        elif tile["owner"] == 1:
            color = (100, 100, 200)

        if tile["type"] == "chance":
            color = (255, 215, 0)

        pygame.draw.circle(screen, color, (x, y), 14)

        # players
        for idx, p in enumerate(players):
            if p["pos"] == i:
                offset = idx * 6
                pygame.draw.circle(screen, (255, 0, 0) if idx == 0 else (0, 0, 255),
                                   (x + offset, y + offset), 5)


# ======================
# 主迴圈
# ======================
running = True

while running:
    screen.fill((25, 25, 25))

    draw_board()
    roll_btn.draw()

    # UI
    y = 520
    for p in players:
        txt = BIG.render(f"{p['name']} Money: ${p['money']}", True, (255, 255, 255))
        screen.blit(txt, (50, y))
        y += 40

    msg = FONT.render(message, True, (255, 255, 0))
    screen.blit(msg, (50, 640))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:
                steps = roll_dice()
                move_player(steps)
                handle_tile()
                switch_turn()

            if event.key == pygame.K_b:
                result = buy_tile()
                message = result

        if event.type == pygame.MOUSEBUTTONDOWN:
            if roll_btn.clicked(event.pos):
                steps = roll_dice()
                move_player(steps)
                handle_tile()
                switch_turn()

    clock.tick(30)

pygame.quit()
sys.exit()