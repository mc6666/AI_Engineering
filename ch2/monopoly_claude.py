import pygame
import random
import sys
import math

pygame.init()

# ── 常數設定 ──────────────────────────────────────────────────
WIDTH, HEIGHT = 900, 900
FPS = 60

# 顏色
WHITE     = (255, 255, 255)
BLACK     = (10,  10,  10)
BG_COLOR  = (240, 235, 215)
BOARD_BG  = (255, 252, 235)
GOLD      = (212, 175, 55)
DARKGOLD  = (160, 120, 20)
RED       = (200, 50,  50)
GREEN     = (60,  160, 60)
BLUE      = (50,  100, 200)
ORANGE    = (230, 130, 30)
PURPLE    = (140, 50,  180)
CYAN      = (30,  180, 200)
PINK      = (220, 100, 150)
GRAY      = (160, 160, 160)
LIGHTGRAY = (210, 210, 210)
DARKGRAY  = (80,  80,  80)
YELLOW    = (240, 200, 0)
TEAL      = (0,   150, 136)
CREAM     = (255, 248, 220)

PLAYER_COLORS = [(220, 60, 60), (60, 100, 220), (60, 180, 60), (200, 130, 30)]
PLAYER_NAMES  = ["玩家 1", "玩家 2", "玩家 3", "玩家 4"]

# ── 棋盤格子定義 ──────────────────────────────────────────────
# type: go/property/tax/chance/jail/goto_jail/free/utility/railroad
SQUARES = [
    {"name": "出發", "type": "go", "color": None, "price": 0, "rent": [0]},
    {"name": "台北101", "type": "property", "color": TEAL, "price": 600, "rent": [50,250,750,2250,3500,5000]},
    {"name": "命運", "type": "chance", "color": None, "price": 0, "rent": [0]},
    {"name": "新竹科學園區", "type": "property", "color": TEAL, "price": 600, "rent": [60,300,900,2700,4000,5500]},
    {"name": "所得稅", "type": "tax", "color": None, "price": 200, "rent": [0]},
    {"name": "台灣高鐵", "type": "railroad", "color": None, "price": 2000, "rent": [250,500,1000,2000]},
    {"name": "台中國家歌劇院", "type": "property", "color": PINK, "price": 1000, "rent": [90,450,1250,3750,5250,7000]},
    {"name": "機會", "type": "chance", "color": None, "price": 0, "rent": [0]},
    {"name": "高雄展覽館", "type": "property", "color": PINK, "price": 1000, "rent": [90,450,1250,3750,5250,7000]},
    {"name": "花蓮太魯閣", "type": "property", "color": PINK, "price": 1200, "rent": [100,500,1500,4500,6250,7500]},
    {"name": "監獄探訪", "type": "jail", "color": None, "price": 0, "rent": [0]},
    {"name": "日月潭風景區", "type": "property", "color": ORANGE, "price": 1400, "rent": [110,550,1650,5000,7500,9750]},
    {"name": "台電公司", "type": "utility", "color": None, "price": 1500, "rent": [0]},
    {"name": "阿里山國家公園", "type": "property", "color": ORANGE, "price": 1400, "rent": [110,550,1650,5000,7500,9750]},
    {"name": "墾丁國家公園", "type": "property", "color": ORANGE, "price": 1600, "rent": [120,600,1800,5500,8250,11000]},
    {"name": "普悠瑪號", "type": "railroad", "color": None, "price": 2000, "rent": [250,500,1000,2000]},
    {"name": "士林夜市", "type": "property", "color": RED, "price": 1800, "rent": [140,700,2000,5500,7500,9500]},
    {"name": "命運", "type": "chance", "color": None, "price": 0, "rent": [0]},
    {"name": "饒河街夜市", "type": "property", "color": RED, "price": 1800, "rent": [140,700,2000,5500,7500,9500]},
    {"name": "逢甲夜市", "type": "property", "color": RED, "price": 2000, "rent": [150,750,2250,6000,8500,11250]},
    {"name": "免費停車", "type": "free", "color": None, "price": 0, "rent": [0]},
    {"name": "西門町商圈", "type": "property", "color": YELLOW, "price": 2200, "rent": [180,900,2500,7000,9750,12750]},
    {"name": "機會", "type": "chance", "color": None, "price": 0, "rent": [0]},
    {"name": "信義計畫區", "type": "property", "color": YELLOW, "price": 2200, "rent": [180,900,2500,7000,9750,12750]},
    {"name": "東區商圈", "type": "property", "color": YELLOW, "price": 2400, "rent": [200,1000,3000,7500,10500,13500]},
    {"name": "自強號", "type": "railroad", "color": None, "price": 2000, "rent": [250,500,1000,2000]},
    {"name": "忠孝東路", "type": "property", "color": GREEN, "price": 2600, "rent": [220,1100,3300,8000,9750,11500]},
    {"name": "仁愛路", "type": "property", "color": GREEN, "price": 2600, "rent": [220,1100,3300,8000,9750,11500]},
    {"name": "台灣自來水", "type": "utility", "color": None, "price": 1500, "rent": [0]},
    {"name": "敦化南路", "type": "property", "color": GREEN, "price": 2800, "rent": [240,1200,3600,8500,10250,12000]},
    {"name": "去坐牢", "type": "goto_jail", "color": None, "price": 0, "rent": [0]},
    {"name": "大安森林公園", "type": "property", "color": BLUE, "price": 3500, "rent": [350,1750,5000,11000,13000,15000]},
    {"name": "陽明山國家公園", "type": "property", "color": BLUE, "price": 3500, "rent": [350,1750,5000,11000,13000,15000]},
    {"name": "命運", "type": "chance", "color": None, "price": 0, "rent": [0]},
    {"name": "總統府", "type": "property", "color": BLUE, "price": 4000, "rent": [500,2000,6000,14000,17000,20000]},
    {"name": "捷運公司", "type": "railroad", "color": None, "price": 2000, "rent": [250,500,1000,2000]},
    {"name": "機會", "type": "chance", "color": None, "price": 0, "rent": [0]},
    {"name": "台北故宮", "type": "property", "color": PURPLE, "price": 3500, "rent": [350,1750,5000,11000,13000,15000]},
    {"name": "奢侈稅", "type": "tax", "color": None, "price": 100, "rent": [0]},
    {"name": "國立中正紀念堂", "type": "property", "color": PURPLE, "price": 4000, "rent": [500,2000,6000,14000,17000,20000]},
]

CHANCE_CARDS = [
    ("前進至出發，領取 $2000", "advance_go"),
    ("銀行利息，收取 $500", "collect", 500),
    ("繳交稅款 $300", "pay", 300),
    ("前進三格", "move", 3),
    ("退後三格", "move", -3),
    ("全體玩家各給你 $100", "collect_all", 100),
    ("房屋維修費，每棟繳 $250", "pay_houses", 250),
    ("出獄卡（保留備用）", "jail_free"),
    ("前進至最近的鐵路", "nearest_railroad"),
    ("收取紅利 $1000", "collect", 1000),
]

# ── 版面計算 ──────────────────────────────────────────────────
BOARD_MARGIN = 40
BOARD_SIZE   = WIDTH - 2 * BOARD_MARGIN   # 820
CORNER_SIZE  = 110
NUM_SIDE     = 9   # 每邊非角落格子數
CELL_W  = (BOARD_SIZE - 2 * CORNER_SIZE) // NUM_SIDE   # ~66
CELL_H  = CORNER_SIZE

# 計算每格中心座標 (順時針，從左下角=出發開始)
def get_square_rect(idx):
    bx, by = BOARD_MARGIN, BOARD_MARGIN
    bs = BOARD_SIZE
    cs = CORNER_SIZE
    cw = CELL_W

    if idx == 0:   # 右下角（出發）
        return pygame.Rect(bx+bs-cs, by+bs-cs, cs, cs)
    elif 1 <= idx <= 9:   # 底邊 右→左
        col = 9 - idx
        return pygame.Rect(bx+cs+col*cw, by+bs-cs, cw, cs)
    elif idx == 10:  # 左下角（監獄）
        return pygame.Rect(bx, by+bs-cs, cs, cs)
    elif 11 <= idx <= 19:  # 左邊 下→上
        row = idx - 10
        return pygame.Rect(bx, by+bs-cs-row*cw, cs, cw)
    elif idx == 20:  # 左上角（免費停車）
        return pygame.Rect(bx, by, cs, cs)
    elif 21 <= idx <= 29:  # 上邊 左→右
        col = idx - 20
        return pygame.Rect(bx+cs+(col-1)*cw, by, cw, cs)
    elif idx == 30:  # 右上角（去坐牢）
        return pygame.Rect(bx+bs-cs, by, cs, cs)
    elif 31 <= idx <= 39:  # 右邊 上→下
        row = idx - 30
        return pygame.Rect(bx+bs-cs, by+cs+(row-1)*cw, cs, cw)
    return pygame.Rect(0, 0, 0, 0)


def get_square_center(idx):
    r = get_square_rect(idx)
    return r.centerx, r.centery


# ── 玩家類別 ──────────────────────────────────────────────────
class Player:
    def __init__(self, pid):
        self.pid      = pid
        self.name     = PLAYER_NAMES[pid]
        self.color    = PLAYER_COLORS[pid]
        self.money    = 15000
        self.pos      = 0
        self.in_jail  = False
        self.jail_turns = 0
        self.bankrupt = False
        self.jail_free_cards = 0
        self.owned    = []   # 擁有的格子 index 列表
        self.houses   = {}   # {square_idx: num_houses}

    def pay(self, amount, game):
        if self.money >= amount:
            self.money -= amount
            return True
        # 嘗試變賣資產
        self.money -= amount
        if self.money < 0:
            self.bankrupt = True
        return not self.bankrupt

    def receive(self, amount):
        self.money += amount


# ── 主遊戲類別 ────────────────────────────────────────────────
class MonopolyGame:
    def __init__(self, num_players=2):
        self.screen  = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("大富翁 Monopoly")
        self.clock   = pygame.time.Clock()
        # self.font_lg = pygame.font.SysFont("notosanscjktc", 22, bold=True)
        # self.font_md = pygame.font.SysFont("notosanscjktc", 16)
        # self.font_sm = pygame.font.SysFont("notosanscjktc", 12)
        self.font_lg = pygame.font.Font("kaiu.ttf", 24)
        self.font_md = pygame.font.Font("kaiu.ttf", 18)
        self.font_sm = pygame.font.Font("kaiu.ttf", 16)
        # fallback fonts
        # for fname in ["notosanscjktc","microsoftyahei","arialms","arial"]:
            # try:
                # self.font_lg = pygame.font.SysFont(fname, 22, bold=True)
                # self.font_md = pygame.font.SysFont(fname, 16)
                # self.font_sm = pygame.font.SysFont(fname, 12)
                # break
            # except:
                # pass

        self.num_players = num_players
        self.players  = [Player(i) for i in range(num_players)]
        self.current  = 0
        self.dice     = (0, 0)
        self.phase    = "roll"   # roll / move / action / buy / end_turn
        self.message  = []
        self.anim_pos = None   # (player, target_pos, steps)
        self.anim_timer = 0
        self.squares_data = [{"owner": None, "houses": 0} for _ in SQUARES]
        self.show_buy_dialog = False
        self.buy_square_idx  = -1
        self.jail_free_used  = False

    # ── 骰子 ──────────────────────────────────────────────────
    def roll_dice(self):
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        self.dice = (d1, d2)
        return d1 + d2

    # ── 消息系統 ──────────────────────────────────────────────
    def add_msg(self, text):
        self.message.append(text)
        if len(self.message) > 6:
            self.message.pop(0)

    # ── 處理落地事件 ──────────────────────────────────────────
    def handle_landing(self, player):
        sq  = SQUARES[player.pos]
        sdata = self.squares_data[player.pos]
        self.add_msg(f"{player.name} 落在 [{sq['name']}]")

        if sq["type"] == "go":
            player.receive(2000)
            self.add_msg("經過出發！領取 $2000")

        elif sq["type"] == "goto_jail":
            player.pos      = 10
            player.in_jail  = True
            player.jail_turns = 0
            self.add_msg(f"{player.name} 被送進監獄！")

        elif sq["type"] == "tax":
            tax = sq["price"]
            player.pay(tax, self)
            self.add_msg(f"繳稅 ${tax}")

        elif sq["type"] == "chance":
            self.draw_chance(player)

        elif sq["type"] in ("property", "railroad", "utility"):
            if sdata["owner"] is None:
                # 可購買
                if sq["price"] > 0:
                    self.show_buy_dialog = True
                    self.buy_square_idx  = player.pos
            elif sdata["owner"] != player.pid:
                # 繳租金
                owner  = self.players[sdata["owner"]]
                rent   = self.calc_rent(player.pos, sdata)
                player.pay(rent, self)
                owner.receive(rent)
                self.add_msg(f"繳租金 ${rent} 給 {owner.name}")

    def calc_rent(self, idx, sdata):
        sq = SQUARES[idx]
        if sq["type"] == "railroad":
            owner = self.players[sdata["owner"]]
            count = sum(1 for i, s in enumerate(self.squares_data)
                        if SQUARES[i]["type"] == "railroad" and s["owner"] == owner.pid)
            return sq["rent"][min(count-1, 3)]
        elif sq["type"] == "utility":
            count = sum(1 for i, s in enumerate(self.squares_data)
                        if SQUARES[i]["type"] == "utility" and s["owner"] == sdata["owner"])
            roll  = sum(self.dice)
            return roll * (4 if count == 1 else 10)
        else:
            h = sdata["houses"]
            return sq["rent"][min(h, len(sq["rent"])-1)]

    def draw_chance(self, player):
        card = random.choice(CHANCE_CARDS)
        self.add_msg(f"🎴 {card[0]}")
        action = card[1]
        if action == "advance_go":
            player.pos = 0
            player.receive(2000)
        elif action == "collect":
            player.receive(card[2])
        elif action == "pay":
            player.pay(card[2], self)
        elif action == "move":
            player.pos = (player.pos + card[2]) % 40
            self.handle_landing(player)
        elif action == "collect_all":
            for p in self.players:
                if p.pid != player.pid and not p.bankrupt:
                    p.pay(card[2], self)
                    player.receive(card[2])
        elif action == "pay_houses":
            total = sum(v for v in self.squares_data[i]["houses"]
                        for i in range(40)
                        if self.squares_data[i]["owner"] == player.pid)
            player.pay(total * card[2], self)
        elif action == "jail_free":
            player.jail_free_cards += 1
        elif action == "nearest_railroad":
            # find next railroad
            pos = player.pos
            for step in range(1, 41):
                npos = (pos + step) % 40
                if SQUARES[npos]["type"] == "railroad":
                    player.pos = npos
                    self.handle_landing(player)
                    break

    # ── 購買格子 ──────────────────────────────────────────────
    def buy_property(self, player, idx):
        sq = SQUARES[idx]
        if player.money >= sq["price"]:
            player.pay(sq["price"], self)
            self.squares_data[idx]["owner"] = player.pid
            player.owned.append(idx)
            self.add_msg(f"{player.name} 購買 {sq['name']} (${ sq['price']})")
            return True
        self.add_msg("錢不夠！無法購買")
        return False

    # ── 下一位玩家 ────────────────────────────────────────────
    def next_turn(self):
        self.show_buy_dialog = False
        active = [p for p in self.players if not p.bankrupt]
        if len(active) <= 1:
            self.phase = "gameover"
            return
        n = (self.current + 1) % self.num_players
        while self.players[n].bankrupt:
            n = (n + 1) % self.num_players
        self.current = n
        self.phase   = "roll"
        self.add_msg(f"─── {self.players[n].name} 的回合 ───")

    def current_player(self):
        return self.players[self.current]

    # ── 移動動畫 (簡化：直接到位) ─────────────────────────────
    def move_player(self, player, steps):
        old = player.pos
        new = (old + steps) % 40
        # 經過出發
        if new < old or (old + steps) >= 40:
            if not player.in_jail:
                player.receive(2000)
                self.add_msg(f"{player.name} 經過出發，領取 $2000")
        player.pos = new

    # ── 主循環 ────────────────────────────────────────────────
    def run(self):
        self.add_msg("🎲 大富翁開始！")
        self.add_msg(f"─── {self.players[0].name} 的回合 ───")
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            self.draw()
        pygame.quit()
        sys.exit()

    def handle_click(self, pos):
        player = self.current_player()
        if self.phase == "gameover":
            return

        # 購買對話框
        if self.show_buy_dialog:
            buy_rect  = pygame.Rect(WIDTH//2-120, HEIGHT//2-60, 100, 44)
            skip_rect = pygame.Rect(WIDTH//2+20,  HEIGHT//2-60, 100, 44)
            if buy_rect.collidepoint(pos):
                self.buy_property(player, self.buy_square_idx)
                self.show_buy_dialog = False
                self.phase = "end_turn"
            elif skip_rect.collidepoint(pos):
                self.show_buy_dialog = False
                self.phase = "end_turn"
            return

        # 擲骰子按鈕
        roll_btn  = pygame.Rect(WIDTH//2-190, HEIGHT//2+200, 120, 44)
        end_btn   = pygame.Rect(WIDTH//2+70,  HEIGHT//2+200, 120, 44)
        house_btn = pygame.Rect(WIDTH//2-60,  HEIGHT//2+200, 120, 44)

        if self.phase == "roll" and roll_btn.collidepoint(pos):
            if player.in_jail:
                self.handle_jail_roll(player)
            else:
                steps = self.roll_dice()
                self.add_msg(f"{player.name} 擲出 {self.dice[0]}+{self.dice[1]}={steps}")
                self.move_player(player, steps)
                self.handle_landing(player)
                if not self.show_buy_dialog:
                    self.phase = "end_turn"

        elif self.phase == "end_turn" and end_btn.collidepoint(pos):
            self.next_turn()

        elif self.phase == "end_turn" and house_btn.collidepoint(pos):
            self.try_build_house(player)

    def handle_jail_roll(self, player):
        steps = self.roll_dice()
        self.add_msg(f"{player.name} 在獄中擲出 {self.dice[0]}+{self.dice[1]}")
        if self.dice[0] == self.dice[1]:
            player.in_jail = False
            self.add_msg("骰出雙數！出獄！")
            self.move_player(player, steps)
            self.handle_landing(player)
        else:
            player.jail_turns += 1
            if player.jail_turns >= 3:
                player.in_jail = False
                player.pay(500, self)
                self.add_msg("繳罰款 $500 出獄")
                self.move_player(player, steps)
                self.handle_landing(player)
            else:
                self.add_msg(f"未出獄，剩 {3-player.jail_turns} 次機會")
        if not self.show_buy_dialog:
            self.phase = "end_turn"

    def try_build_house(self, player):
        # 找一塊可以蓋房子的地
        for idx in player.owned:
            sq = SQUARES[idx]
            if sq["type"] == "property":
                sdata = self.squares_data[idx]
                if sdata["houses"] < 5:
                    cost = sq["price"] // 2
                    if player.money >= cost:
                        player.pay(cost, self)
                        sdata["houses"] += 1
                        h = ["","一棟","二棟","三棟","四棟","飯店"][sdata["houses"]]
                        self.add_msg(f"在 {sq['name']} 蓋了{h}房子 (${cost})")
                        return
        self.add_msg("目前無法蓋房子")

    # ── 繪製 ──────────────────────────────────────────────────
    def draw(self):
        self.screen.fill(BG_COLOR)
        self.draw_board()
        self.draw_players()
        self.draw_ui()
        if self.show_buy_dialog:
            self.draw_buy_dialog()
        if self.phase == "gameover":
            self.draw_gameover()
        pygame.display.flip()

    def draw_board(self):
        bx, by = BOARD_MARGIN, BOARD_MARGIN
        bs = BOARD_SIZE

        # 棋盤底色
        pygame.draw.rect(self.screen, BOARD_BG, (bx, by, bs, bs))
        pygame.draw.rect(self.screen, DARKGOLD, (bx, by, bs, bs), 4)

        # 中央裝飾
        cx, cy = bx + bs//2, by + bs//2
        inner = bs - 2 * CORNER_SIZE - 2 * CELL_W
        ir = pygame.Rect(cx - inner//2, cy - inner//2, inner, inner)
        pygame.draw.rect(self.screen, CREAM, ir, border_radius=8)
        pygame.draw.rect(self.screen, GOLD, ir, 3, border_radius=8)
        title = self.font_lg.render("大 富 翁", True, DARKGOLD)
        self.screen.blit(title, (cx - title.get_width()//2, cy - 40))
        sub = self.font_sm.render("MONOPOLY", True, GOLD)
        self.screen.blit(sub, (cx - sub.get_width()//2, cy - 10))
        # 繪製骰子
        if self.dice[0] > 0:
            self.draw_dice_icon(cx - 40, cy + 20, self.dice[0])
            self.draw_dice_icon(cx + 10, cy + 20, self.dice[1])

        # 畫每個格子
        for i, sq in enumerate(SQUARES):
            rect = get_square_rect(i)
            self.draw_square(rect, sq, i)

    def draw_dice_icon(self, x, y, val):
        r = pygame.Rect(x, y, 26, 26)
        pygame.draw.rect(self.screen, WHITE, r, border_radius=4)
        pygame.draw.rect(self.screen, DARKGRAY, r, 2, border_radius=4)
        dots = {
            1: [(13,13)],
            2: [(7,7),(19,19)],
            3: [(7,7),(13,13),(19,19)],
            4: [(7,7),(19,7),(7,19),(19,19)],
            5: [(7,7),(19,7),(13,13),(7,19),(19,19)],
            6: [(7,6),(19,6),(7,13),(19,13),(7,20),(19,20)],
        }
        for dx, dy in dots.get(val, []):
            pygame.draw.circle(self.screen, BLACK, (x+dx, y+dy), 3)

    def draw_square(self, rect, sq, idx):
        sdata = self.squares_data[idx]

        # 格子底色
        bg = WHITE
        if sq["type"] == "go":
            bg = (230, 255, 230)
        elif sq["type"] == "jail":
            bg = (255, 240, 200)
        elif sq["type"] == "goto_jail":
            bg = (255, 210, 210)
        elif sq["type"] == "free":
            bg = (210, 240, 255)
        elif sq["type"] == "tax":
            bg = (255, 230, 230)
        elif sq["type"] == "chance":
            bg = (240, 230, 255)
        elif sq["type"] == "railroad":
            bg = (230, 230, 230)
        elif sq["type"] == "utility":
            bg = (225, 255, 225)

        # 若有主人，微微著色
        if sdata["owner"] is not None:
            oc = PLAYER_COLORS[sdata["owner"]]
            bg = tuple(min(255, int(bg[i]*0.7 + oc[i]*0.3)) for i in range(3))

        pygame.draw.rect(self.screen, bg, rect)
        pygame.draw.rect(self.screen, DARKGRAY, rect, 1)

        # 顏色條（地產）
        if sq["color"] and sq["type"] == "property":
            is_corner = (idx in [0,10,20,30])
            if not is_corner:
                if 0 < idx < 10 or 20 < idx < 30:   # 水平格
                    bar = pygame.Rect(rect.x, rect.y, rect.width, 14)
                else:                                  # 垂直格
                    bar = pygame.Rect(rect.x, rect.y, 14, rect.height)
                pygame.draw.rect(self.screen, sq["color"], bar)

        # 文字
        name = sq["name"]
        is_corner = (idx in [0,10,20,30])
        if is_corner:
            self.draw_corner_text(rect, sq, idx)
        else:
            # 判斷橫/直
            if rect.width > rect.height:   # 水平格（上下邊）
                lines = self.wrap_text(name, self.font_sm, rect.width - 4)
                start_y = rect.y + 18
                for line in lines[:3]:
                    surf = self.font_sm.render(line, True, BLACK)
                    self.screen.blit(surf, (rect.centerx - surf.get_width()//2, start_y))
                    start_y += 13
                # 價格
                if sq["price"] > 0:
                    ps = self.font_sm.render(f"${sq['price']}", True, DARKGRAY)
                    self.screen.blit(ps, (rect.centerx - ps.get_width()//2, rect.bottom - 15))
            else:   # 垂直格（左右邊）
                lines = self.wrap_text(name, self.font_sm, rect.height - 4)
                # 旋轉繪製
                surf = pygame.Surface((rect.height, rect.width), pygame.SRCALPHA)
                start_y2 = 14
                for line in lines[:3]:
                    ts = self.font_sm.render(line, True, BLACK)
                    surf.blit(ts, (surf.get_width()//2 - ts.get_width()//2, start_y2))
                    start_y2 += 13
                if sq["price"] > 0:
                    ps2 = self.font_sm.render(f"${sq['price']}", True, DARKGRAY)
                    surf.blit(ps2, (surf.get_width()//2 - ps2.get_width()//2, surf.get_height()-16))
                if idx < 20:   # 左邊：向右轉90
                    rotated = pygame.transform.rotate(surf, -90)
                else:          # 右邊：向左轉90
                    rotated = pygame.transform.rotate(surf, 90)
                self.screen.blit(rotated, (rect.x + rect.width//2 - rotated.get_width()//2,
                                           rect.y + rect.height//2 - rotated.get_height()//2))

        # 房屋小圖示
        if sdata["houses"] > 0:
            self.draw_houses(rect, sdata["houses"], idx)

    def draw_corner_text(self, rect, sq, idx):
        icons = {0: "🏁", 10: "🔒", 20: "🅿️", 30: "⛓️"}
        labels = {0: "出發\n領$2000", 10: "監獄\n探訪", 20: "免費\n停車", 30: "去\n坐牢"}
        icon_t = self.font_md.render(sq["name"][:2], True, DARKGOLD)
        self.screen.blit(icon_t, (rect.centerx - icon_t.get_width()//2, rect.centery - 20))
        sub = self.font_sm.render(sq["name"][2:] if len(sq["name"]) > 2 else "", True, DARKGRAY)
        self.screen.blit(sub, (rect.centerx - sub.get_width()//2, rect.centery + 4))

    def wrap_text(self, text, font, max_w):
        lines, line = [], ""
        for ch in text:
            test = line + ch
            if font.size(test)[0] <= max_w:
                line = test
            else:
                lines.append(line)
                line = ch
        if line:
            lines.append(line)
        return lines

    def draw_houses(self, rect, count, idx):
        color = GREEN if count < 5 else RED
        if rect.width > rect.height:
            sx = rect.x + 2
            for i in range(count):
                pygame.draw.rect(self.screen, color, (sx + i*10, rect.bottom - 28, 8, 8))
        else:
            sy = rect.y + 2
            for i in range(count):
                pygame.draw.rect(self.screen, color, (rect.right - 12, sy + i*10, 8, 8))

    def draw_players(self):
        # 計算同一格多個玩家的偏移
        pos_groups = {}
        for p in self.players:
            if not p.bankrupt:
                pos_groups.setdefault(p.pos, []).append(p)

        for pos, group in pos_groups.items():
            cx, cy = get_square_center(pos)
            offsets = [(-10, -10), (10, -10), (-10, 10), (10, 10)]
            for i, p in enumerate(group):
                ox, oy = offsets[i % 4]
                self.draw_token(cx + ox, cy + oy, p)

    def draw_token(self, x, y, player):
        # 光暈
        pygame.draw.circle(self.screen, (*player.color[:3], 80), (x, y), 14)
        pygame.draw.circle(self.screen, player.color, (x, y), 11)
        pygame.draw.circle(self.screen, WHITE, (x, y), 11, 2)
        # 編號
        n = self.font_sm.render(str(player.pid + 1), True, WHITE)
        self.screen.blit(n, (x - n.get_width()//2, y - n.get_height()//2))
        # 目前玩家閃爍環
        if player.pid == self.current and not player.bankrupt:
            t  = pygame.time.get_ticks() // 300 % 2
            if t == 0:
                pygame.draw.circle(self.screen, GOLD, (x, y), 15, 3)

    def draw_ui(self):
        # 右側 UI 面板（棋盤中央區域下方用按鈕，資訊顯示在中央）
        cx = WIDTH // 2
        cy = BOARD_MARGIN + BOARD_SIZE // 2

        # 玩家資訊卡
        panel_x = cx - 200
        panel_y = cy - 180
        panel_w = 400
        panel_h = 160
        pygame.draw.rect(self.screen, (255,255,255,200), (panel_x, panel_y, panel_w, panel_h), border_radius=10)
        pygame.draw.rect(self.screen, GOLD, (panel_x, panel_y, panel_w, panel_h), 2, border_radius=10)

        title = self.font_md.render("玩家資產", True, DARKGOLD)
        self.screen.blit(title, (cx - title.get_width()//2, panel_y + 6))

        for i, p in enumerate(self.players):
            row_y = panel_y + 30 + i * 30
            col_x = panel_x + 10 + (i % 2) * 200
            row_y2 = panel_y + 30 + (i // 2) * 30
            col_x2 = panel_x + 10 + (i % 2) * 200

            pygame.draw.circle(self.screen, p.color, (col_x2 + 8, row_y2 + 10), 8)
            if p.pid == self.current and not p.bankrupt:
                pygame.draw.circle(self.screen, GOLD, (col_x2 + 8, row_y2 + 10), 10, 2)

            status = "（破產）" if p.bankrupt else ("（監獄）" if p.in_jail else "")
            txt = f"{p.name}: ${p.money:,} {status}"
            color_t = RED if p.bankrupt else (DARKGOLD if p.pid == self.current else DARKGRAY)
            s = self.font_sm.render(txt, True, color_t)
            self.screen.blit(s, (col_x2 + 22, row_y2 + 3))

        # 消息框
        msg_x = cx - 200
        msg_y = panel_y + panel_h + 8
        msg_w = 400
        msg_h = 100
        pygame.draw.rect(self.screen, (245, 245, 235), (msg_x, msg_y, msg_w, msg_h), border_radius=6)
        pygame.draw.rect(self.screen, LIGHTGRAY, (msg_x, msg_y, msg_w, msg_h), 1, border_radius=6)
        for j, m in enumerate(self.message[-5:]):
            ms = self.font_sm.render(m, True, DARKGRAY)
            self.screen.blit(ms, (msg_x + 6, msg_y + 4 + j * 18))

        # 按鈕
        btn_y  = cy + 200
        player = self.current_player()

        if self.phase == "roll":
            label = "🎲 擲骰子（坐牢）" if player.in_jail else "🎲 擲骰子"
            self.draw_button(cx - 190, btn_y, 200, 44, label, GREEN)
        elif self.phase == "end_turn":
            self.draw_button(cx + 70, btn_y, 130, 44, "下一位 ▶", BLUE)
            if any(SQUARES[i]["type"] == "property" and
                   self.squares_data[i]["owner"] == player.pid and
                   self.squares_data[i]["houses"] < 5
                   for i in player.owned):
                self.draw_button(cx - 60, btn_y, 120, 44, "🏠 蓋房子", ORANGE)

        # 目前回合提示
        turn_txt = self.font_md.render(
            f"目前回合：{player.name}  |  第 {player.pos+1} 格：{SQUARES[player.pos]['name']}",
            True, DARKGOLD
        )
        self.screen.blit(turn_txt, (cx - turn_txt.get_width()//2, btn_y + 54))

    def draw_button(self, x, y, w, h, text, color):
        pygame.draw.rect(self.screen, color, (x, y, w, h), border_radius=8)
        pygame.draw.rect(self.screen, WHITE, (x, y, w, h), 2, border_radius=8)
        t = self.font_md.render(text, True, WHITE)
        self.screen.blit(t, (x + w//2 - t.get_width()//2, y + h//2 - t.get_height()//2))

    def draw_buy_dialog(self):
        sq = SQUARES[self.buy_square_idx]
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 130))
        self.screen.blit(overlay, (0, 0))

        dw, dh = 380, 200
        dx = WIDTH//2 - dw//2
        dy = HEIGHT//2 - dh//2 - 20
        pygame.draw.rect(self.screen, CREAM, (dx, dy, dw, dh), border_radius=12)
        pygame.draw.rect(self.screen, GOLD, (dx, dy, dw, dh), 3, border_radius=12)

        t1 = self.font_lg.render(f"購買 {sq['name']}？", True, DARKGOLD)
        self.screen.blit(t1, (WIDTH//2 - t1.get_width()//2, dy + 16))
        t2 = self.font_md.render(f"售價：${sq['price']:,}", True, DARKGRAY)
        self.screen.blit(t2, (WIDTH//2 - t2.get_width()//2, dy + 56))
        t3 = self.font_sm.render(f"你的資金：${self.current_player().money:,}", True, DARKGRAY)
        self.screen.blit(t3, (WIDTH//2 - t3.get_width()//2, dy + 84))

        self.draw_button(WIDTH//2-120, dy+120, 100, 44, "✅ 購買", GREEN)
        self.draw_button(WIDTH//2+20,  dy+120, 100, 44, "❌ 放棄", RED)

    def draw_gameover(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        active = [p for p in self.players if not p.bankrupt]
        winner = max(active, key=lambda p: p.money) if active else None

        dw, dh = 440, 240
        dx = WIDTH//2 - dw//2
        dy = HEIGHT//2 - dh//2
        pygame.draw.rect(self.screen, CREAM, (dx, dy, dw, dh), border_radius=16)
        pygame.draw.rect(self.screen, GOLD, (dx, dy, dw, dh), 4, border_radius=16)

        t1 = self.font_lg.render("遊戲結束！", True, DARKGOLD)
        self.screen.blit(t1, (WIDTH//2 - t1.get_width()//2, dy + 24))
        if winner:
            t2 = self.font_lg.render(f"🏆 {winner.name} 獲勝！", True, PLAYER_COLORS[winner.pid])
            self.screen.blit(t2, (WIDTH//2 - t2.get_width()//2, dy + 70))
            t3 = self.font_md.render(f"資產：${winner.money:,}", True, DARKGRAY)
            self.screen.blit(t3, (WIDTH//2 - t3.get_width()//2, dy + 110))
        t4 = self.font_sm.render("按 ESC 結束遊戲", True, GRAY)
        self.screen.blit(t4, (WIDTH//2 - t4.get_width()//2, dy + 170))


# ── 玩家人數選擇畫面 ──────────────────────────────────────────
def choose_players():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("大富翁 - 開始遊戲")

    # try:
        # font_xl = pygame.font.SysFont("notosanscjktc", 52, bold=True)
        # font_lg = pygame.font.SysFont("notosanscjktc", 28, bold=True)
        # font_md = pygame.font.SysFont("notosanscjktc", 20)
    # except:
        # font_xl = pygame.font.SysFont(None, 52, bold=True)
        # font_lg = pygame.font.SysFont(None, 28, bold=True)
        # font_md = pygame.font.SysFont(None, 20)
    font_xl = pygame.font.Font("kaiu.ttf", 52)
    font_lg = pygame.font.Font("kaiu.ttf", 28)
    font_md = pygame.font.Font("kaiu.ttf", 20)

    clock = pygame.time.Clock()
    while True:
        screen.fill(BG_COLOR)

        # 裝飾背景
        for i in range(8):
            alpha_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surf, (*GOLD, 15), (100 + i*120, 200 + (i%3)*150), 80 + i*20)
            screen.blit(alpha_surf, (0, 0))

        # 標題
        t1 = font_xl.render("大 富 翁", True, DARKGOLD)
        screen.blit(t1, (WIDTH//2 - t1.get_width()//2, 120))
        t2 = font_lg.render("M O N O P O L Y", True, GOLD)
        screen.blit(t2, (WIDTH//2 - t2.get_width()//2, 190))

        pygame.draw.line(screen, GOLD, (200, 240), (700, 240), 2)

        t3 = font_md.render("選擇玩家人數", True, DARKGRAY)
        screen.blit(t3, (WIDTH//2 - t3.get_width()//2, 290))

        buttons = []
        for n in range(2, 5):
            bw, bh = 160, 60
            bx = WIDTH//2 - 240 + (n-2)*180
            by = 360
            rect = pygame.Rect(bx, by, bw, bh)
            buttons.append((rect, n))
            hover = rect.collidepoint(pygame.mouse.get_pos())
            bg = DARKGOLD if hover else GOLD
            pygame.draw.rect(screen, bg, rect, border_radius=12)
            pygame.draw.rect(screen, WHITE, rect, 2, border_radius=12)
            # 玩家圓點
            for i in range(n):
                px2 = bx + bw//2 - (n-1)*14 + i*28
                pygame.draw.circle(screen, PLAYER_COLORS[i], (px2, by+20), 8)
            lbl = font_md.render(f"{n} 人遊戲", True, WHITE)
            screen.blit(lbl, (bx + bw//2 - lbl.get_width()//2, by + 34))

        hint = font_md.render("每位玩家初始資金：$15,000", True, GRAY)
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 470))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for rect, n in buttons:
                    if rect.collidepoint(event.pos):
                        return n

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    num = choose_players()
    game = MonopolyGame(num_players=num)
    game.run()