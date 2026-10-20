from __future__ import annotations

import os
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import pygame


WIDTH_FALLBACK = 1440
HEIGHT_FALLBACK = 900
FPS = 60
PLAYER_MIN = 2
PLAYER_MAX = 5
START_CASH = 500
WIN_NET_WORTH = 1000
BUILD_COST = 200
BAIL_COST = 200
HOUSE_CAP = 3


Color = tuple[int, int, int]


WHITE: Color = (245, 245, 245)
BLACK: Color = (20, 20, 20)
GREEN: Color = (58, 127, 64)
RED: Color = (178, 58, 58)
BLUE: Color = (64, 104, 178)
GOLD: Color = (202, 165, 70)
PANEL: Color = (30, 38, 52)
PANEL_ALT: Color = (41, 51, 70)
PANEL_LIGHT: Color = (59, 72, 97)
TEXT_LIGHT: Color = (236, 241, 248)
TEXT_DIM: Color = (175, 186, 198)
HIGHLIGHT: Color = (90, 174, 228)


def clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))


def wrap_text(font: pygame.font.Font, text: str, width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if font.size(candidate)[0] <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    for name in [
        "Microsoft JhengHei",
        "Noto Sans CJK TC",
        "Arial Unicode MS",
        "SimHei",
        "DejaVu Sans",
        None,
    ]:
        try:
            return pygame.font.SysFont(name, size, bold=bold) if name else pygame.font.Font(None, size)
        except Exception:
            continue
    return pygame.font.Font(None, size)


@dataclass
class Card:
    title: str
    description: str
    action: Callable[["MonopolyGame"], None]


@dataclass
class Tile:
    index: int
    name: str
    kind: str
    price: int = 0
    owner: Optional[int] = None
    houses: int = 0

    @property
    def rentable(self) -> bool:
        return self.kind == "land"

    @property
    def base_rent(self) -> int:
        return int(round(self.price * 0.2))

    @property
    def rent(self) -> int:
        return self.base_rent * (1 + self.houses) if self.rentable else 0

    def asset_name(self) -> str:
        return self.kind


@dataclass
class Player:
    name: str
    color: Color
    cash: int = START_CASH
    position: int = 0
    in_jail: bool = False
    get_out_of_jail: int = 0
    eliminated: bool = False

    def net_worth(self, tiles: list[Tile]) -> int:
        total = self.cash
        identity = id(self)
        for tile in tiles:
            if tile.owner == identity:
                total += tile.price + tile.houses * BUILD_COST
        return total


@dataclass
class Button:
    rect: pygame.Rect
    text: str
    callback: Callable[[], None]
    enabled: bool = True
    accent: Color = BLUE

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, mouse_pos: tuple[int, int]) -> None:
        hovered = self.rect.collidepoint(mouse_pos)
        color = self.accent if self.enabled else PANEL_LIGHT
        if hovered and self.enabled:
            color = tuple(min(255, channel + 24) for channel in color)
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=12)
        label = font.render(self.text, True, WHITE if self.enabled else TEXT_DIM)
        surface.blit(label, label.get_rect(center=self.rect.center))

    def handle(self, event: pygame.event.Event) -> bool:
        if self.enabled and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.callback()
            return True
        return False


class AssetManager:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.images: dict[tuple[str, tuple[int, int] | None], pygame.Surface] = {}
        self.sounds: dict[str, Optional[pygame.mixer.Sound]] = {}
        self.audio_ok = True
        self.music_started = False

    def asset_path(self, *parts: str) -> Path:
        return self.root.joinpath(*parts)

    def load_image(self, path: Path, size: Optional[tuple[int, int]] = None) -> Optional[pygame.Surface]:
        key = (str(path), size)
        if key in self.images:
            return self.images[key]
        if not path.exists():
            return None
        try:
            image = pygame.image.load(str(path)).convert_alpha()
            if size:
                image = pygame.transform.smoothscale(image, size)
            self.images[key] = image
            return image
        except Exception:
            return None

    def tile_image(self, tile: Tile, size: tuple[int, int], index: int) -> Optional[pygame.Surface]:
        candidates = [
            self.asset_path("assets", "tiles", f"{index:02d}.png"),
            self.asset_path("assets", "tiles", f"{tile.kind}.png"),
            self.asset_path("assets", "images", f"{tile.asset_name()}.png"),
            self.asset_path("assets", "images", "tile.png"),
        ]
        for candidate in candidates:
            image = self.load_image(candidate, size)
            if image is not None:
                return image
        return None

    def load_sound(self, key: str, filenames: list[Path]) -> Optional[pygame.mixer.Sound]:
        if key in self.sounds:
            return self.sounds[key]
        for filename in filenames:
            if filename.exists():
                try:
                    sound = pygame.mixer.Sound(str(filename))
                    self.sounds[key] = sound
                    return sound
                except Exception:
                    continue
        self.sounds[key] = None
        return None

    def play_sound(self, key: str, filenames: list[Path], volume: float = 1.0) -> None:
        if not self.audio_ok:
            return
        sound = self.load_sound(key, filenames)
        if sound is None:
            return
        try:
            sound.set_volume(volume)
            sound.play()
        except Exception:
            self.audio_ok = False

    def play_music(self, filenames: list[Path], volume: float = 0.45) -> None:
        if not self.audio_ok or self.music_started:
            return
        for filename in filenames:
            if filename.exists():
                try:
                    pygame.mixer.music.load(str(filename))
                    pygame.mixer.music.set_volume(volume)
                    pygame.mixer.music.play(-1)
                    self.music_started = True
                    return
                except Exception:
                    continue


class MonopolyGame:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.clock = pygame.time.Clock()
        self.root = Path(__file__).resolve().parent
        self.assets = AssetManager(self.root)
        self.font_small = get_font(18)
        self.font_body = get_font(24)
        self.font_title = get_font(34, bold=True)
        self.font_huge = get_font(72, bold=True)
        self.font_menu = get_font(28, bold=True)
        self.random = random.Random()
        self.state = "menu"
        self.menu_player_count = 2
        self.players: list[Player] = []
        self.tiles: list[Tile] = self.create_tiles()
        self.turn_index = 0
        self.active_tile_rects: list[pygame.Rect] = []
        self.message_log: list[str] = []
        self.banner_text = ""
        self.banner_timer = 0.0
        self.pending_move_steps = 0
        self.pending_move_direction = 1
        self.move_step_timer = 0.0
        self.move_after_action: Optional[Callable[[], None]] = None
        self.current_roll = 0
        self.current_roll_label = ""
        self.roll_bounce = 0.0
        self.awaiting_end_turn = False
        self.pending_prompt: Optional[str] = None
        self.pending_prompt_tile: Optional[int] = None
        self.current_prompt_buttons: list[Button] = []
        self.board_origin = (0, 0)
        self.tile_size = (0, 0)
        self.tile_margin = 12
        self.setup_common_sounds()
        self.setup_menu_buttons()
        self.prepare_board_geometry()
        self.start_background_music()

    def setup_common_sounds(self) -> None:
        self.dice_paths = [
            self.root / "assets" / "sounds" / "dice.wav",
            self.root / "assets" / "sounds" / "dice.ogg",
        ]
        self.chance_paths = [
            self.root / "assets" / "sounds" / "chance.wav",
            self.root / "assets" / "sounds" / "card.wav",
            self.root / "assets" / "sounds" / "flip.wav",
        ]
        self.jail_paths = [
            self.root / "assets" / "sounds" / "jail.wav",
            self.root / "assets" / "sounds" / "prison.wav",
        ]
        self.release_paths = [
            self.root / "assets" / "sounds" / "release.wav",
            self.root / "assets" / "sounds" / "jail_out.wav",
        ]
        self.music_paths = [
            self.root / "assets" / "music" / "background.ogg",
            self.root / "assets" / "music" / "background.mp3",
            self.root / "assets" / "music" / "bgm.ogg",
        ]

    def start_background_music(self) -> None:
        self.assets.play_music(self.music_paths)

    def create_tiles(self) -> list[Tile]:
        data = [
            ("起點", "start", 0),
            ("商業街", "land", 200),
            ("機會", "chance", 0),
            ("河濱大道", "land", 220),
            ("機會", "chance", 0),
            ("市中心", "land", 240),
            ("命運", "fate", 0),
            ("港口", "land", 260),
            ("監獄", "jail", 0),
            ("科技園", "land", 280),
            ("空地", "land", 200),
            ("機會", "chance", 0),
            ("觀光區", "land", 300),
            ("命運", "fate", 0),
            ("學區", "land", 320),
            ("療養區", "land", 340),
            ("停車場", "land", 200),
            ("機會", "chance", 0),
            ("工業區", "land", 360),
            ("休閒區", "land", 380),
        ]
        return [Tile(index=index, name=name, kind=kind, price=price) for index, (name, kind, price) in enumerate(data)]

    def setup_menu_buttons(self) -> None:
        center_x = self.width // 2
        center_y = self.height // 2
        self.menu_buttons: list[Button] = []
        for offset, count in enumerate(range(PLAYER_MIN, PLAYER_MAX + 1)):
            x = center_x - 230 + offset * 110
            rect = pygame.Rect(x, center_y + 80, 95, 50)
            self.menu_buttons.append(Button(rect, f"{count} 人", lambda c=count: self.set_menu_count(c), accent=GREEN))
        start_rect = pygame.Rect(center_x - 120, center_y + 160, 240, 58)
        self.menu_buttons.append(Button(start_rect, "開始遊戲", self.begin_game, accent=BLUE))

    def set_menu_count(self, count: int) -> None:
        self.menu_player_count = clamp(count, PLAYER_MIN, PLAYER_MAX)
        self.banner(f"已選擇 {self.menu_player_count} 位玩家")

    def begin_game(self) -> None:
        colors: list[Color] = [RED, BLUE, GREEN, GOLD, (182, 98, 204)]
        self.players = [Player(name=f"玩家 {i + 1}", color=colors[i % len(colors)]) for i in range(self.menu_player_count)]
        self.turn_index = 0
        self.message_log.clear()
        for tile in self.tiles:
            tile.owner = None
            tile.houses = 0
        self.state = "turn_ready"
        self.banner(f"遊戲開始，{self.current_player().name} 先手")
        self.log("每位玩家初始資金 $500。")
        self.log("擲骰後依地圖前進，先達成勝利條件者獲勝。")

    def current_player(self) -> Player:
        self.turn_index %= len(self.players)
        return self.players[self.turn_index]

    def panel_geometry(self) -> tuple[int, int, int, int]:
        panel_x = 28
        panel_y = 28
        panel_w = min(430, self.width // 3)
        panel_h = self.height - 56
        return panel_x, panel_y, panel_w, panel_h

    def prepare_board_geometry(self) -> None:
        panel_x, panel_y, panel_w, panel_h = self.panel_geometry()
        available_width = max(1, self.width - (panel_x + panel_w) - 56)
        available_height = max(1, panel_h)
        tile_side = min(
            max(1, (available_width - self.tile_margin * 5) // 6),
            max(1, (available_height - self.tile_margin * 5) // 6),
        )
        self.tile_size = (tile_side, tile_side)
        board_width = self.tile_size[0] * 6 + self.tile_margin * 5
        board_height = self.tile_size[1] * 6 + self.tile_margin * 5
        board_x = panel_x + panel_w + 28
        board_y = max(28, panel_y + (panel_h - board_height) // 2)
        self.board_origin = (board_x, board_y)
        self.active_tile_rects = self.compute_tile_rects(board_x, board_y)

    def compute_tile_rects(self, board_x: int, board_y: int) -> list[pygame.Rect]:
        tile_w, tile_h = self.tile_size
        gap = self.tile_margin
        rects: list[pygame.Rect] = []
        row_width = tile_w * 5 + gap * 4
        col_height = tile_h * 5 + gap * 4
        left = board_x
        top = board_y
        right = left + row_width - tile_w
        bottom = top + col_height - tile_h
        for index in range(5):
            rects.append(pygame.Rect(left + index * (tile_w + gap), top, tile_w, tile_h))
        for index in range(5):
            rects.append(pygame.Rect(right, top + index * (tile_h + gap), tile_w, tile_h))
        for index in range(5):
            rects.append(pygame.Rect(right - index * (tile_w + gap), bottom, tile_w, tile_h))
        for index in range(5):
            rects.append(pygame.Rect(left, bottom - index * (tile_h + gap), tile_w, tile_h))
        return rects

    def log(self, message: str) -> None:
        self.message_log.append(message)
        self.message_log = self.message_log[-8:]

    def banner(self, message: str, duration: float = 2.1) -> None:
        self.banner_text = message
        self.banner_timer = duration

    def start_turn(self) -> None:
        player = self.current_player()
        self.pending_prompt = None
        self.pending_prompt_tile = None
        self.current_prompt_buttons = []
        self.current_roll = 0
        self.current_roll_label = ""
        self.awaiting_end_turn = False
        if player.in_jail:
            self.state = "jail_turn"
            self.banner(f"{player.name} 在監獄中")
            self.log(f"{player.name} 在監獄中，這回合先處理出獄。")
        else:
            self.state = "turn_ready"
            self.banner(f"輪到 {player.name}")

    def roll_dice(self, jail_attempt: bool = False) -> None:
        if self.state not in {"turn_ready", "jail_turn"}:
            return
        player = self.current_player()
        self.assets.play_sound("dice", self.dice_paths, 0.9)
        self.current_roll = self.random.randint(1, 6)
        self.current_roll_label = f"骰子點數：{self.current_roll}"
        self.roll_bounce = 0.35
        self.log(f"{player.name} 擲出 {self.current_roll} 點。")
        if player.in_jail and jail_attempt:
            if self.current_roll == 6:
                player.in_jail = False
                self.assets.play_sound("release", self.release_paths, 0.9)
                self.banner(f"{player.name} 擲到 6，成功出獄")
                self.log(f"{player.name} 出獄並前進 6 步。")
                self.start_move(6, source="jail_release")
            else:
                self.banner(f"{player.name} 未擲到 6，仍留在監獄")
                self.log(f"{player.name} 本回合無法出獄。")
                self.end_turn()
            return
        self.start_move(self.current_roll, source="dice")

    def use_jail_pass(self) -> None:
        player = self.current_player()
        if not player.in_jail or player.get_out_of_jail <= 0:
            return
        player.get_out_of_jail -= 1
        player.in_jail = False
        self.assets.play_sound("release", self.release_paths, 0.9)
        self.banner(f"{player.name} 使用免獄通行證")
        self.log(f"{player.name} 使用免獄通行證離開監獄。")
        self.state = "turn_ready"

    def pay_bail(self) -> None:
        player = self.current_player()
        if not player.in_jail or player.cash < BAIL_COST:
            return
        player.cash -= BAIL_COST
        player.in_jail = False
        self.assets.play_sound("release", self.release_paths, 0.9)
        self.banner(f"{player.name} 支付 $200 保釋金")
        self.log(f"{player.name} 支付保釋金 $200。")
        self.check_elimination(player)
        if player.eliminated:
            self.end_turn()
            return
        self.state = "turn_ready"

    def start_move(self, steps: int, source: str = "dice") -> None:
        if steps == 0:
            self.resolve_landing(source=source)
            return
        self.pending_move_steps = abs(steps)
        self.pending_move_direction = 1 if steps > 0 else -1
        self.move_step_timer = 0.12
        self.move_after_action = lambda: self.finish_move_source(source)
        self.state = "moving"
        self.log(f"{self.current_player().name} 開始移動 {steps} 步。")

    def finish_move_source(self, source: str) -> None:
        if source == "dice":
            self.log(f"{self.current_player().name} 完成擲骰移動。")
        elif source == "card":
            self.log(f"{self.current_player().name} 完成卡片移動。")
        elif source == "jail_release":
            self.log(f"{self.current_player().name} 因出獄前進 6 步。")
        self.resolve_landing(source=source)

    def move_one_step(self) -> None:
        player = self.current_player()
        player.position = (player.position + self.pending_move_direction) % len(self.tiles)
        self.pending_move_steps -= 1
        self.current_roll_label = f"位置：{self.tiles[player.position].name}"

    def draw_card(self, cards: list[Card], deck_name: str) -> None:
        card = self.random.choice(cards)
        sound_key = "chance" if deck_name == "機會" else "fate"
        self.assets.play_sound(sound_key, self.chance_paths, 0.8)
        self.log(f"抽到{deck_name}：{card.title}。")
        self.banner(f"{deck_name}卡：{card.title}")
        card.action(self)

    def get_chance_cards(self) -> list[Card]:
        return [
            Card("前進 5 步", "前進 5 步。", lambda g: g.start_move(5, source="card")),
            Card("後退 3 步", "後退 3 步。", lambda g: g.start_move(-3, source="card")),
            Card("銀行派發紅利 $100", "獲得 $100。", lambda g: g.current_player_add_cash(100)),
            Card("獲得獎券獎金 $500", "獲得 $500。", lambda g: g.current_player_add_cash(500)),
            Card("房屋修繕費 $100", "支付 $100。", lambda g: g.current_player_pay(100)),
            Card("所得稅 $200", "支付 $200。", lambda g: g.current_player_pay(200)),
            Card("直接進監獄", "立刻進入監獄。", lambda g: g.send_to_jail(g.current_player(), "機會卡")),
            Card("免獄通行證一張", "獲得一張免獄通行證。", lambda g: g.current_player_gain_pass()),
            Card("每位玩家付你 $50", "向每位玩家收 $50。", lambda g: g.collect_from_everyone(50)),
            Card("付每位玩家 $50", "每位玩家收你 $50。", lambda g: g.pay_everyone(50)),
        ]

    def get_fate_cards(self) -> list[Card]:
        return [
            Card("銀行錯誤多付 $200", "獲得 $200。", lambda g: g.current_player_add_cash(200)),
            Card("生日禮金", "每位玩家送你 $10。", lambda g: g.collect_from_everyone(10)),
            Card("醫院費用 $100", "支付 $100。", lambda g: g.current_player_pay(100)),
            Card("學費 $100", "支付 $100。", lambda g: g.current_player_pay(100)),
            Card("直接進監獄", "立刻進入監獄。", lambda g: g.send_to_jail(g.current_player(), "命運卡")),
            Card("免獄通行證一張", "獲得一張免獄通行證。", lambda g: g.current_player_gain_pass()),
        ]

    def resolve_landing(self, source: str) -> None:
        player = self.current_player()
        tile = self.tiles[player.position]
        self.log(f"{player.name} 停在 {tile.name}。")
        if tile.kind == "start":
            self.banner(f"{player.name} 停在起點")
            self.after_landing()
            return
        if tile.kind == "chance":
            self.draw_card(self.get_chance_cards(), "機會")
            return
        if tile.kind == "fate":
            self.draw_card(self.get_fate_cards(), "命運")
            return
        if tile.kind == "jail":
            self.send_to_jail(player, cause="停到監獄")
            self.after_landing()
            return
        if tile.rentable:
            owner = self.player_by_identity(tile.owner) if tile.owner is not None else None
            if tile.owner is None or owner is None:
                tile.owner = None
                self.prepare_purchase_prompt(tile.index)
                return
            if owner is player:
                self.banner(f"停在自己的土地：{tile.name}")
                self.after_landing()
                return
            rent = tile.rent
            self.log(f"{player.name} 需支付 {owner.name} 過路費 $ {rent}。")
            self.banner(f"支付 {owner.name} $ {rent}")
            self.transfer_cash(player, owner, rent)
            if player.eliminated:
                self.end_turn()
                return
            self.after_landing()
            return
        self.after_landing()

    def after_landing(self) -> None:
        self.awaiting_end_turn = True
        self.state = "turn_ready"
        self.check_win_conditions()

    def prepare_purchase_prompt(self, tile_index: int) -> None:
        tile = self.tiles[tile_index]
        player = self.current_player()
        self.pending_prompt = "purchase"
        self.pending_prompt_tile = tile_index
        self.state = "prompt"
        center_x = self.width // 2
        center_y = self.height // 2
        buy_rect = pygame.Rect(center_x - 250, center_y + 120, 160, 54)
        skip_rect = pygame.Rect(center_x - 80, center_y + 120, 160, 54)
        auction_rect = pygame.Rect(center_x + 90, center_y + 120, 160, 54)
        self.current_prompt_buttons = [
            Button(buy_rect, f"購買 $ {tile.price}", lambda: self.buy_tile(tile_index), enabled=player.cash >= tile.price, accent=GREEN),
            Button(skip_rect, "先不買", self.skip_purchase, accent=PANEL_LIGHT),
            Button(auction_rect, "拍賣", self.auction_tile, enabled=len(self.alive_players()) > 1, accent=GOLD),
        ]
        self.banner(f"可購買 {tile.name}，價格 $ {tile.price}")
        self.log(f"{player.name} 抵達可購地產 {tile.name}。")

    def skip_purchase(self) -> None:
        self.pending_prompt = None
        self.pending_prompt_tile = None
        self.current_prompt_buttons = []
        self.banner("未購買土地")
        self.after_landing()

    def buy_tile(self, tile_index: int) -> None:
        player = self.current_player()
        tile = self.tiles[tile_index]
        if tile.owner is not None or not tile.rentable or player.cash < tile.price:
            return
        player.cash -= tile.price
        tile.owner = self.player_identity(player)
        tile.houses = 0
        self.log(f"{player.name} 以 $ {tile.price} 購買 {tile.name}。")
        self.banner(f"{player.name} 成為 {tile.name} 擁有者")
        self.finish_prompt_resolution()
        self.check_elimination(player)
        if player.eliminated:
            self.end_turn()
            return

    def auction_tile(self) -> None:
        tile_index = self.pending_prompt_tile
        if tile_index is None:
            return
        tile = self.tiles[tile_index]
        candidates = [player for player in self.alive_players() if player is not self.current_player() and player.cash >= tile.price]
        if not candidates:
            self.log(f"{tile.name} 無人出價，維持未售出。")
            self.banner(f"{tile.name} 無人拍下")
            self.skip_purchase()
            return
        winner = max(candidates, key=lambda candidate: candidate.cash)
        winner.cash -= tile.price
        tile.owner = self.player_identity(winner)
        tile.houses = 0
        self.log(f"{tile.name} 由 {winner.name} 以原價 $ {tile.price} 拍下。")
        self.banner(f"拍賣成交：{winner.name}")
        self.check_elimination(winner)
        self.finish_prompt_resolution()

    def finish_prompt_resolution(self) -> None:
        self.pending_prompt = None
        self.pending_prompt_tile = None
        self.current_prompt_buttons = []
        self.after_landing()

    def build_house(self) -> None:
        player = self.current_player()
        tile = self.tiles[player.position]
        if not tile.rentable or tile.owner != self.player_identity(player):
            return
        if tile.houses >= HOUSE_CAP or player.cash < BUILD_COST:
            return
        player.cash -= BUILD_COST
        tile.houses += 1
        self.log(f"{player.name} 在 {tile.name} 興建房屋，現有 {tile.houses} 間。")
        self.banner(f"{tile.name} 增建 1 間房屋")
        self.check_elimination(player)
        if player.eliminated:
            self.end_turn()
            return
        self.check_win_conditions()

    def current_player_add_cash(self, amount: int) -> None:
        player = self.current_player()
        player.cash += amount
        self.log(f"{player.name} 收入 $ {amount}。")
        self.banner(f"{player.name} 獲得 $ {amount}")

    def current_player_pay(self, amount: int) -> None:
        player = self.current_player()
        self.transfer_cash(player, None, amount)
        if player.eliminated:
            self.end_turn()

    def current_player_gain_pass(self) -> None:
        player = self.current_player()
        player.get_out_of_jail += 1
        self.log(f"{player.name} 獲得免獄通行證。")
        self.banner(f"{player.name} 得到免獄通行證")

    def collect_from_everyone(self, amount: int) -> None:
        collector = self.current_player()
        for player in self.alive_players():
            if player is collector:
                continue
            self.transfer_cash(player, collector, amount, silent=True)
        self.log(f"{collector.name} 向每位玩家收取 $ {amount}。")
        self.banner(f"{collector.name} 收到多人付款")

    def pay_everyone(self, amount: int) -> None:
        payer = self.current_player()
        for player in self.alive_players():
            if player is payer:
                continue
            self.transfer_cash(payer, player, amount, silent=True)
            if payer.eliminated:
                break
        self.log(f"{payer.name} 支付每位玩家 $ {amount}。")
        self.banner(f"{payer.name} 向所有人付款")

    def transfer_cash(self, payer: Player, payee: Optional[Player], amount: int, silent: bool = False) -> None:
        payer.cash -= amount
        if payee is not None:
            payee.cash += amount
        if not silent:
            if payee is None:
                self.log(f"{payer.name} 支付 $ {amount}。")
            else:
                self.log(f"{payer.name} 支付 $ {amount} 給 {payee.name}。")
        self.check_elimination(payer)
        if payee is not None:
            self.check_elimination(payee)
        if payer.eliminated and payer is self.current_player() and self.state not in {"menu", "game_over"}:
            self.end_turn()

    def send_to_jail(self, player: Player, cause: str) -> None:
        player.in_jail = True
        player.position = 8
        self.assets.play_sound("jail", self.jail_paths, 0.9)
        self.banner(f"{player.name} 進入監獄")
        self.log(f"{player.name} 因 {cause} 進入監獄。")

    def player_identity(self, player: Player) -> int:
        return id(player)

    def player_by_identity(self, identity: int) -> Optional[Player]:
        for player in self.players:
            if id(player) == identity and not player.eliminated:
                return player
        return None

    def alive_players(self) -> list[Player]:
        return [player for player in self.players if not player.eliminated]

    def check_elimination(self, player: Player) -> None:
        if player.eliminated:
            return
        if player.cash > 0:
            return
        player.eliminated = True
        player.cash = 0
        self.log(f"{player.name} 資金歸零，退出遊戲。")
        self.banner(f"{player.name} 被淘汰")
        self.auction_player_properties(player)

    def auction_player_properties(self, player: Player) -> None:
        identity = self.player_identity(player)
        for tile in self.tiles:
            if tile.owner != identity:
                continue
            tile.owner = None
            tile.houses = 0
            candidates = [candidate for candidate in self.alive_players() if candidate is not player and candidate.cash >= tile.price]
            if not candidates:
                self.log(f"{tile.name} 回到銀行。")
                continue
            winner = max(candidates, key=lambda candidate: candidate.cash)
            winner.cash -= tile.price
            tile.owner = self.player_identity(winner)
            self.log(f"{tile.name} 以原價 $ {tile.price} 轉讓給 {winner.name}。")

    def check_win_conditions(self) -> None:
        alive = self.alive_players()
        if len(alive) == 1 and self.players:
            self.state = "game_over"
            self.banner(f"{alive[0].name} 獲勝")
            return
        for player in alive:
            if player.net_worth(self.tiles) >= WIN_NET_WORTH:
                self.state = "game_over"
                self.banner(f"{player.name} 資產達標獲勝")
                return

    def end_turn(self) -> None:
        if not self.players or self.state == "game_over" or self.state == "moving":
            return
        self.pending_prompt = None
        self.pending_prompt_tile = None
        self.current_prompt_buttons = []
        self.awaiting_end_turn = False
        self.turn_index = (self.turn_index + 1) % len(self.players)
        while self.players and self.current_player().eliminated:
            self.turn_index = (self.turn_index + 1) % len(self.players)
        self.start_turn()

    def can_build_house(self) -> bool:
        if not self.players:
            return False
        player = self.current_player()
        tile = self.tiles[player.position]
        return tile.rentable and tile.owner == self.player_identity(player) and tile.houses < HOUSE_CAP and player.cash >= BUILD_COST

    def restart_game(self) -> None:
        self.players = []
        for tile in self.tiles:
            tile.owner = None
            tile.houses = 0
        self.message_log.clear()
        self.state = "menu"
        self.banner("重新開始")
        self.setup_menu_buttons()

    def get_action_buttons(self) -> list[Button]:
        buttons: list[Button] = []
        if self.state == "turn_ready" and self.players:
            base_x = self.width // 2 - 250
            base_y = self.height - 135
            buttons.append(Button(pygame.Rect(base_x, base_y, 160, 54), "擲骰子", self.roll_dice, accent=BLUE))
            if self.can_build_house():
                buttons.append(Button(pygame.Rect(base_x + 170, base_y, 160, 54), "興建房屋", self.build_house, accent=GREEN))
            buttons.append(Button(pygame.Rect(base_x + 340, base_y, 160, 54), "結束回合", self.end_turn, accent=PANEL_LIGHT, enabled=self.awaiting_end_turn))
        elif self.state == "jail_turn" and self.players:
            player = self.current_player()
            base_x = self.width // 2 - 250
            base_y = self.height - 135
            buttons.append(Button(pygame.Rect(base_x, base_y, 160, 54), "用通行證", self.use_jail_pass, accent=GREEN, enabled=player.get_out_of_jail > 0))
            buttons.append(Button(pygame.Rect(base_x + 170, base_y, 160, 54), "繳保釋金", self.pay_bail, accent=GOLD, enabled=player.cash >= BAIL_COST))
            buttons.append(Button(pygame.Rect(base_x + 340, base_y, 160, 54), "擲骰 6 出獄", lambda: self.roll_dice(jail_attempt=True), accent=BLUE))
        elif self.state == "game_over":
            buttons.append(Button(pygame.Rect(self.width // 2 - 80, self.height - 135, 160, 54), "重新開始", self.restart_game, accent=GREEN))
        return buttons

    def draw_background(self) -> None:
        self.screen.fill((15, 22, 33))
        for i in range(9):
            alpha = 18 + i * 4
            band = pygame.Surface((self.width, 80), pygame.SRCALPHA)
            band.fill((34, 44, 61, alpha))
            self.screen.blit(band, (0, i * 100))
        pygame.draw.circle(self.screen, (34, 54, 82), (self.width - 240, 160), 160)
        pygame.draw.circle(self.screen, (27, 35, 54), (self.width - 140, self.height - 140), 180)

    def board_surface(self, tile_index: int, rect: pygame.Rect) -> pygame.Surface:
        tile = self.tiles[tile_index]
        surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        base = (63, 72, 92)
        if tile.kind == "start":
            base = (68, 130, 94)
        elif tile.kind == "chance":
            base = (76, 118, 191)
        elif tile.kind == "fate":
            base = (156, 98, 194)
        elif tile.kind == "jail":
            base = (186, 93, 75)
        elif tile.owner is not None:
            owner = self.player_by_identity(tile.owner)
            if owner:
                base = tuple(int(channel * 0.62 + owner.color[i] * 0.38) for i, channel in enumerate(base))
        surface.fill(base)
        pygame.draw.rect(surface, WHITE, surface.get_rect(), 3, border_radius=10)
        return surface

    def draw_player_tokens(self) -> None:
        offsets = [(-14, -14), (14, -14), (-14, 14), (14, 14), (0, 0)]
        for tile_index, rect in enumerate(self.active_tile_rects):
            players_here = [player for player in self.players if not player.eliminated and player.position == tile_index]
            for index, player in enumerate(players_here):
                off_x, off_y = offsets[index % len(offsets)]
                center = (rect.centerx + off_x, rect.centery + off_y)
                pygame.draw.circle(self.screen, BLACK, center, 11)
                pygame.draw.circle(self.screen, player.color, center, 9)
                marker = self.font_small.render(str(self.players.index(player) + 1), True, WHITE)
                self.screen.blit(marker, marker.get_rect(center=center))

    def draw_board(self) -> None:
        for index, rect in enumerate(self.active_tile_rects):
            tile = self.tiles[index]
            tile_surface = self.board_surface(index, rect)
            image = self.assets.tile_image(tile, rect.size, index)
            if image is not None:
                tile_surface.blit(image, (0, 0))
            label_font = self.font_small if rect.width < 120 else self.font_body
            name_lines = wrap_text(label_font, tile.name, rect.width - 16)
            for line_no, line in enumerate(name_lines[:2]):
                label = label_font.render(line, True, WHITE)
                tile_surface.blit(label, (8, 8 + line_no * (label_font.get_height() + 2)))
            if tile.kind == "land":
                price = label_font.render(f"$ {tile.price}", True, GOLD)
                rent = label_font.render(f"租金 $ {tile.rent}", True, TEXT_LIGHT)
                tile_surface.blit(price, (8, rect.height - price.get_height() * 2 - 2))
                tile_surface.blit(rent, (8, rect.height - rent.get_height() - 4))
                if tile.houses:
                    house_text = label_font.render(f"房屋 x{tile.houses}", True, (247, 223, 159))
                    tile_surface.blit(house_text, (rect.width - house_text.get_width() - 8, rect.height - house_text.get_height() - 4))
            self.screen.blit(tile_surface, rect)
            pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=10)
        self.draw_player_tokens()

    def draw_menu(self, panel_x: int, panel_y: int) -> None:
        self.screen.blit(self.font_menu.render("選擇 2 ~ 5 人", True, TEXT_LIGHT), (panel_x + 20, panel_y))
        info = [
            f"目前選擇：{self.menu_player_count} 人",
            "每人初始資金 $500",
            "按下「開始遊戲」進入全螢幕地圖",
        ]
        y = panel_y + 42
        for line in info:
            self.screen.blit(self.font_small.render(line, True, TEXT_DIM), (panel_x + 22, y))
            y += 26
        mouse = pygame.mouse.get_pos()
        for button in self.menu_buttons:
            button.draw(self.screen, self.font_small, mouse)

    def draw_side_panel(self) -> None:
        panel_x, panel_y, panel_w, panel_h = self.panel_geometry()
        panel = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(self.screen, PANEL, panel, border_radius=20)
        pygame.draw.rect(self.screen, PANEL_LIGHT, panel, 2, border_radius=20)
        self.screen.blit(self.font_title.render("大富翁", True, TEXT_LIGHT), (panel_x + 20, panel_y + 16))
        self.screen.blit(self.font_small.render("PyGame OOP Prototype", True, TEXT_DIM), (panel_x + 22, panel_y + 58))
        if self.state == "menu":
            self.draw_menu(panel_x, panel_y + 96)
            return
        if self.players:
            current = self.current_player()
            current_box = pygame.Rect(panel_x + 18, panel_y + 96, panel_w - 36, 118)
            pygame.draw.rect(self.screen, PANEL_ALT, current_box, border_radius=16)
            self.screen.blit(self.font_body.render(f"回合：{current.name}", True, current.color), (current_box.x + 16, current_box.y + 14))
            self.screen.blit(self.font_body.render(f"現金：$ {current.cash}", True, WHITE), (current_box.x + 16, current_box.y + 48))
            self.screen.blit(self.font_body.render(f"淨資產：$ {current.net_worth(self.tiles)}", True, GOLD), (current_box.x + 16, current_box.y + 78))
            status_lines = [
                f"位置：{self.tiles[current.position].name}",
                f"監獄：{'是' if current.in_jail else '否'}",
                f"免獄通行證：{current.get_out_of_jail}",
                f"骰子：{self.current_roll_label or '-'}",
            ]
            y = current_box.bottom + 16
            for line in status_lines:
                self.screen.blit(self.font_small.render(line, True, TEXT_LIGHT), (panel_x + 22, y))
                y += 24
        y = panel_y + panel_h - 278
        self.screen.blit(self.font_body.render("玩家列表", True, TEXT_LIGHT), (panel_x + 20, y))
        y += 38
        for index, player in enumerate(self.players):
            row = pygame.Rect(panel_x + 16, y + index * 40, panel_w - 32, 34)
            color = PANEL_ALT if index != self.turn_index or self.state == "game_over" else (54, 71, 100)
            pygame.draw.rect(self.screen, color, row, border_radius=10)
            status = "淘汰" if player.eliminated else ("監獄" if player.in_jail else "活躍")
            text = self.font_small.render(f"{index + 1}. {player.name}  $ {player.cash}  {status}", True, player.color)
            self.screen.blit(text, (row.x + 10, row.y + 8))
        log_box = pygame.Rect(panel_x + 16, panel_y + panel_h - 210, panel_w - 32, 192)
        pygame.draw.rect(self.screen, PANEL_ALT, log_box, border_radius=16)
        self.screen.blit(self.font_body.render("訊息", True, TEXT_LIGHT), (log_box.x + 14, log_box.y + 12))
        line_y = log_box.y + 46
        for line in self.message_log[-6:]:
            for wrapped in wrap_text(self.font_small, line, log_box.width - 20):
                self.screen.blit(self.font_small.render(wrapped, True, TEXT_DIM), (log_box.x + 12, line_y))
                line_y += 22
        if self.banner_timer > 0 and self.banner_text:
            banner_rect = pygame.Rect(self.width // 2 - 260, 22, 520, 54)
            pygame.draw.rect(self.screen, (11, 21, 34), banner_rect, border_radius=16)
            pygame.draw.rect(self.screen, HIGHLIGHT, banner_rect, 2, border_radius=16)
            banner = self.font_body.render(self.banner_text, True, WHITE)
            self.screen.blit(banner, banner.get_rect(center=banner_rect.center))

    def draw_action_buttons(self) -> None:
        buttons = self.current_prompt_buttons if self.state == "prompt" else self.get_action_buttons()
        mouse = pygame.mouse.get_pos()
        for button in buttons:
            button.draw(self.screen, self.font_small, mouse)

    def draw_center_overlay(self) -> None:
        if self.state == "moving":
            number = str(self.current_roll)
            text = self.font_huge.render(number, True, WHITE)
            shadow = self.font_huge.render(number, True, BLACK)
            rect = text.get_rect(center=(self.width // 2, self.height // 2 - 20))
            bounce = int(12 * abs(pygame.math.Vector2(0, 1).rotate(self.roll_bounce * 720).y))
            rect.y -= bounce
            self.screen.blit(shadow, shadow.get_rect(center=(rect.centerx + 3, rect.centery + 4)))
            self.screen.blit(text, rect)
            caption = self.font_body.render("擲骰中", True, TEXT_LIGHT)
            self.screen.blit(caption, caption.get_rect(center=(self.width // 2, self.height // 2 + 64)))
        elif self.state == "game_over":
            overlay = pygame.Rect(self.width // 2 - 240, self.height // 2 - 100, 480, 200)
            pygame.draw.rect(self.screen, (14, 18, 28), overlay, border_radius=20)
            pygame.draw.rect(self.screen, HIGHLIGHT, overlay, 3, border_radius=20)
            alive = self.alive_players()
            if alive:
                winner = alive[0]
                title = self.font_title.render(f"{winner.name} 勝利", True, winner.color)
                self.screen.blit(title, title.get_rect(center=(overlay.centerx, overlay.y + 64)))
                detail = self.font_body.render(f"淨資產 $ {winner.net_worth(self.tiles)}", True, GOLD)
                self.screen.blit(detail, detail.get_rect(center=(overlay.centerx, overlay.y + 118)))
            else:
                title = self.font_title.render("遊戲結束", True, WHITE)
                self.screen.blit(title, title.get_rect(center=overlay.center))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit(0)
            if event.key == pygame.K_RETURN and self.state == "menu":
                self.begin_game()
            if event.key == pygame.K_SPACE:
                if self.state == "turn_ready":
                    self.roll_dice()
                elif self.state == "jail_turn":
                    self.roll_dice(jail_attempt=True)
                elif self.state == "game_over":
                    self.restart_game()
            if event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
        if self.state == "menu":
            for button in self.menu_buttons:
                button.handle(event)
            return
        if self.state == "prompt":
            for button in self.current_prompt_buttons:
                if button.handle(event):
                    return
            return
        for button in self.get_action_buttons():
            if button.handle(event):
                return

    def update(self, dt: float) -> None:
        if self.banner_timer > 0:
            self.banner_timer = max(0.0, self.banner_timer - dt)
        if self.roll_bounce > 0:
            self.roll_bounce = max(0.0, self.roll_bounce - dt)
        if self.state == "moving":
            self.move_step_timer -= dt
            if self.move_step_timer <= 0:
                self.move_step_timer = 0.12
                if self.pending_move_steps > 0:
                    self.move_one_step()
                if self.pending_move_steps <= 0:
                    callback = self.move_after_action
                    self.move_after_action = None
                    self.state = "turn_ready"
                    if callback:
                        callback()
        self.check_win_conditions()

    def draw(self) -> None:
        self.draw_background()
        if self.state != "menu":
            self.draw_board()
        self.draw_side_panel()
        self.draw_action_buttons()
        self.draw_center_overlay()
        if self.state in {"turn_ready", "jail_turn"} and self.players:
            help_text = self.font_small.render("快捷鍵：Space 擲骰，Esc 離開，F11 切換全螢幕", True, TEXT_DIM)
            self.screen.blit(help_text, (self.width // 2 - help_text.get_width() // 2, self.height - 28))
        pygame.display.flip()

    def update_and_draw(self) -> None:
        dt = self.clock.tick(FPS) / 1000.0
        self.update(dt)
        self.draw()

    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                self.handle_event(event)
            self.update_and_draw()


def create_display() -> pygame.Surface:
    os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
    pygame.init()
    try:
        pygame.mixer.init()
    except Exception:
        pass
    try:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.SCALED)
    except Exception:
        screen = pygame.display.set_mode((WIDTH_FALLBACK, HEIGHT_FALLBACK))
    pygame.display.set_caption("大富翁 Monopoly")
    return screen


def main() -> None:
    screen = create_display()
    game = MonopolyGame(screen)
    game.run()


if __name__ == "__main__":
    main()
