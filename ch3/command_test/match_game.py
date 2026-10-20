import tkinter as tk
import random
import math

CARD_SIZE = 95
COLS = 4
ROWS = 4
TOTAL_PAIRS = 8

CARD_TYPES = [
    {"id": 0, "name": "紅心", "color": "#E74C3C", "dark": "#922B21", "shape": "heart"},
    {"id": 1, "name": "藍星", "color": "#3498DB", "dark": "#1A5276", "shape": "star"},
    {"id": 2, "name": "綠鑽", "color": "#2ECC71", "dark": "#1E8449", "shape": "diamond"},
    {"id": 3, "name": "紫圓", "color": "#9B59B6", "dark": "#6C3483", "shape": "circle"},
    {"id": 4, "name": "橙方", "color": "#E67E22", "dark": "#935116", "shape": "square"},
    {"id": 5, "name": "青花", "color": "#1ABC9C", "dark": "#0E6655", "shape": "flower"},
    {"id": 6, "name": "黃月", "color": "#F1C40F", "dark": "#9A7D0A", "shape": "moon"},
    {"id": 7, "name": "粉樹", "color": "#FF69B4", "dark": "#C2185B", "shape": "tree"},
]

BG_DARK   = "#1a1a2e"
BG_PANEL  = "#16213e"
CARD_BACK = "#1e3a5f"
CARD_FRONT = "#f5f5f5"


def draw_shape(canvas, shape, color, dark, size):
    cx, cy = size / 2, size / 2
    r = size * 0.30

    if shape == "heart":
        canvas.create_oval(cx - r,       cy - r * 0.55,
                           cx + r * 0.1, cy + r * 0.65,
                           fill=color, outline=dark, width=2)
        canvas.create_oval(cx - r * 0.1, cy - r * 0.55,
                           cx + r,       cy + r * 0.65,
                           fill=color, outline=dark, width=2)
        canvas.create_polygon(cx - r, cy + r * 0.25,
                              cx + r, cy + r * 0.25,
                              cx,     cy + r * 1.5,
                              fill=color, outline=dark, width=2)

    elif shape == "star":
        pts = []
        for i in range(5):
            a = math.radians(i * 72 - 90)
            pts += [cx + r * math.cos(a), cy + r * math.sin(a)]
            a = math.radians(i * 72 - 90 + 36)
            pts += [cx + r * 0.4 * math.cos(a), cy + r * 0.4 * math.sin(a)]
        canvas.create_polygon(pts, fill=color, outline=dark, width=2)

    elif shape == "diamond":
        canvas.create_polygon(cx,       cy - r * 1.4,
                              cx + r,   cy,
                              cx,       cy + r * 1.4,
                              cx - r,   cy,
                              fill=color, outline=dark, width=2)

    elif shape == "circle":
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                           fill=color, outline=dark, width=3)
        canvas.create_oval(cx - r * 0.45, cy - r * 0.45,
                           cx + r * 0.45, cy + r * 0.45,
                           fill=dark, outline="")

    elif shape == "square":
        canvas.create_rectangle(cx - r, cy - r, cx + r, cy + r,
                                fill=color, outline=dark, width=3)
        canvas.create_rectangle(cx - r * 0.45, cy - r * 0.45,
                                cx + r * 0.45, cy + r * 0.45,
                                fill=dark, outline="")

    elif shape == "flower":
        for i in range(6):
            a = math.radians(i * 60)
            fx = cx + r * 0.58 * math.cos(a)
            fy = cy + r * 0.58 * math.sin(a)
            canvas.create_oval(fx - r * 0.44, fy - r * 0.44,
                               fx + r * 0.44, fy + r * 0.44,
                               fill=color, outline=dark, width=1)
        canvas.create_oval(cx - r * 0.28, cy - r * 0.28,
                           cx + r * 0.28, cy + r * 0.28,
                           fill=dark, outline="")

    elif shape == "moon":
        pts = []
        for deg in range(-150, 151, 5):
            a = math.radians(deg)
            pts += [cx + r * math.cos(a), cy + r * math.sin(a)]
        offset = r * 0.52
        ir = r * 0.80
        for deg in range(150, -151, -5):
            a = math.radians(deg)
            pts += [cx + offset + ir * math.cos(a), cy + ir * math.sin(a)]
        canvas.create_polygon(pts, fill=color, outline=dark, width=2)

    elif shape == "tree":
        canvas.create_polygon(cx,            cy - r * 1.35,
                              cx + r * 0.85, cy + r * 0.15,
                              cx - r * 0.85, cy + r * 0.15,
                              fill=color, outline=dark, width=2)
        canvas.create_polygon(cx,            cy - r * 0.5,
                              cx + r * 1.05, cy + r * 1.05,
                              cx - r * 1.05, cy + r * 1.05,
                              fill=dark, outline=dark, width=1)
        canvas.create_rectangle(cx - r * 0.2, cy + r * 1.05,
                                cx + r * 0.2, cy + r * 1.4,
                                fill="#8B4513", outline="#5D2F0A")


class MatchGame:
    def __init__(self, root):
        self.root = root
        self.root.title("配對記憶力測驗")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(False, False)

        self.cards       = []
        self.flipped     = []
        self.moves       = 0
        self.matched     = 0
        self.seconds     = 0
        self.timer_id    = None
        self.locked      = False
        self.started     = False
        self.best        = None

        self._build_ui()
        self._new_game()

    # ── UI construction ────────────────────────────────────────────────────
    def _build_ui(self):
        tk.Label(self.root, text="配對記憶力測驗",
                 font=("Microsoft JhengHei", 20, "bold"),
                 bg=BG_DARK, fg="#64C8FF").pack(pady=(15, 2))

        tk.Label(self.root, text="點擊翻牌，找出所有相同圖案！",
                 font=("Microsoft JhengHei", 10),
                 bg=BG_DARK, fg="#a0c4ff").pack(pady=(0, 10))

        # Stats bar
        bar = tk.Frame(self.root, bg=BG_PANEL)
        bar.pack(fill="x", padx=20, pady=(0, 8))

        self.v_moves  = tk.StringVar(value="翻牌: 0")
        self.v_pairs  = tk.StringVar(value="配對: 0 / 8")
        self.v_timer  = tk.StringVar(value="時間: 0s")

        for v in (self.v_moves, self.v_pairs, self.v_timer):
            tk.Label(bar, textvariable=v,
                     font=("Microsoft JhengHei", 11, "bold"),
                     bg=BG_PANEL, fg="white").pack(side="left", expand=True, pady=8)

        # Board
        self.board = tk.Frame(self.root, bg="#0d1117")
        self.board.pack(padx=15, pady=4)

        # Message
        self.v_msg = tk.StringVar(value="")
        tk.Label(self.root, textvariable=self.v_msg,
                 font=("Microsoft JhengHei", 12, "bold"),
                 bg=BG_DARK, fg="#FFD700").pack(pady=6)

        # Best time
        self.v_best = tk.StringVar(value="")
        tk.Label(self.root, textvariable=self.v_best,
                 font=("Microsoft JhengHei", 9),
                 bg=BG_DARK, fg="#a0c4ff").pack()

        # Button
        tk.Button(self.root, text="重新開始",
                  font=("Microsoft JhengHei", 11, "bold"),
                  bg="#E94560", fg="white",
                  activebackground="#c73652", activeforeground="white",
                  relief="flat", cursor="hand2",
                  padx=22, pady=7,
                  command=self._new_game).pack(pady=(6, 18))

    # ── Card canvas helpers ────────────────────────────────────────────────
    def _make_canvas(self, parent, ct, back: bool) -> tk.Canvas:
        s = CARD_SIZE
        bg     = CARD_BACK  if back else CARD_FRONT
        border = "#3a6ea5"  if back else ct["dark"]

        c = tk.Canvas(parent, width=s, height=s, bg=bg,
                      highlightthickness=3,
                      highlightbackground=border,
                      cursor="hand2")
        if back:
            c.create_text(s // 2, s // 2, text="?",
                          font=("Arial Black", 28, "bold"), fill="#5b9bd5")
        else:
            draw_shape(c, ct["shape"], ct["color"], ct["dark"], s)
            c.create_text(s // 2, s - 9, text=ct["name"],
                          font=("Microsoft JhengHei", 8, "bold"), fill=ct["dark"])
        return c

    # ── Game logic ─────────────────────────────────────────────────────────
    def _new_game(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        self.flipped  = []
        self.moves    = 0
        self.matched  = 0
        self.seconds  = 0
        self.locked   = False
        self.started  = False

        self.v_moves.set("翻牌: 0")
        self.v_pairs.set("配對: 0 / 8")
        self.v_timer.set("時間: 0s")
        self.v_msg.set("點擊翻牌開始！")
        self._refresh_best()

        for w in self.board.winfo_children():
            w.destroy()
        self.cards = []

        deck = CARD_TYPES * 2
        random.shuffle(deck)

        for i, ct in enumerate(deck):
            row, col = divmod(i, COLS)
            frame = tk.Frame(self.board, bg="#0d1117")
            frame.grid(row=row, column=col, padx=5, pady=5)

            back_c  = self._make_canvas(frame, ct, back=True)
            front_c = self._make_canvas(frame, ct, back=False)
            back_c.pack()

            card = {
                "type_id":  ct["id"],
                "dark":     ct["dark"],
                "frame":    frame,
                "back":     back_c,
                "front":    front_c,
                "flipped":  False,
                "matched":  False,
            }
            self.cards.append(card)

            for canvas in (back_c, front_c):
                canvas.bind("<Button-1>", lambda e, idx=i: self._click(idx))

    def _click(self, idx):
        if self.locked:
            return
        card = self.cards[idx]
        if card["flipped"] or card["matched"]:
            return

        if not self.started:
            self.started = True
            self._tick()

        self._reveal(idx, True)
        self.flipped.append(idx)

        if len(self.flipped) == 2:
            self.locked = True
            self.moves += 1
            self.v_moves.set(f"翻牌: {self.moves}")
            self.root.after(750, self._check)

    def _reveal(self, idx, show_front: bool):
        c = self.cards[idx]
        c["flipped"] = show_front
        if show_front:
            c["back"].pack_forget()
            c["front"].pack()
        else:
            c["front"].pack_forget()
            c["back"].pack()

    def _check(self):
        a, b = self.flipped
        ca, cb = self.cards[a], self.cards[b]

        if ca["type_id"] == cb["type_id"]:
            for c in (ca, cb):
                c["matched"] = True
                c["front"].configure(highlightbackground="#2ECC71",
                                     highlightthickness=4)
            self.matched += 1
            self.v_pairs.set(f"配對: {self.matched} / {TOTAL_PAIRS}")
            if self.matched == TOTAL_PAIRS:
                self.root.after(300, self._win)
        else:
            self._reveal(a, False)
            self._reveal(b, False)

        self.flipped = []
        self.locked  = False

    def _tick(self):
        if self.started and self.matched < TOTAL_PAIRS:
            self.v_timer.set(f"時間: {self.seconds}s")
            self.seconds += 1
            self.timer_id = self.root.after(1000, self._tick)

    def _win(self):
        self.started = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        if self.best is None or self.seconds < self.best:
            self.best = self.seconds

        if   self.moves <= TOTAL_PAIRS + 2: grade = "完美！"
        elif self.moves <= TOTAL_PAIRS * 2: grade = "很棒！"
        else:                               grade = "完成！"

        self.v_msg.set(f"{grade}  用時 {self.seconds} 秒 / 翻牌 {self.moves} 次")
        self._refresh_best()

    def _refresh_best(self):
        self.v_best.set(
            f"最佳記錄：{self.best} 秒" if self.best is not None else ""
        )


if __name__ == "__main__":
    root = tk.Tk()
    MatchGame(root)
    root.mainloop()
