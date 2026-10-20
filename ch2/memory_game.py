import tkinter as tk
from tkinter import messagebox
import random

# =========================
# 配對記憶力遊戲
# =========================

class MemoryGame:
    def __init__(self, root):
        self.root = root
        self.root.title("配對記憶力測驗")

        self.symbols = ['🍎', '🍌', '🍇', '🍒',
                        '🍉', '🥝', '🍍', '🍑']

        self.reset_game()

    # -------------------------
    # 初始化 / 重置遊戲
    # -------------------------
    def reset_game(self):

        self.cards = self.symbols * 2
        random.shuffle(self.cards)

        self.first_card = None
        self.second_card = None

        self.lock = False

        self.moves = 0
        self.matched_pairs = 0

        # 清除舊畫面
        for widget in self.root.winfo_children():
            widget.destroy()

        # 標題
        title = tk.Label(
            self.root,
            text="配對記憶力測驗",
            font=("Arial", 24, "bold")
        )
        title.grid(row=0, column=0, columnspan=4, pady=10)

        # 步數
        self.move_label = tk.Label(
            self.root,
            text=f"步數: {self.moves}",
            font=("Arial", 14)
        )
        self.move_label.grid(row=1, column=0, columnspan=4)

        # 建立卡片按鈕
        self.buttons = []

        index = 0
        for row in range(2, 6):
            for col in range(4):

                btn = tk.Button(
                    self.root,
                    text="?",
                    width=8,
                    height=4,
                    font=("Arial", 18),
                    command=lambda idx=index: self.flip_card(idx)
                )

                btn.grid(row=row, column=col, padx=5, pady=5)

                self.buttons.append(btn)

                index += 1

        # 重新開始按鈕
        restart_btn = tk.Button(
            self.root,
            text="重新開始",
            font=("Arial", 12),
            bg="lightblue",
            command=self.reset_game
        )

        restart_btn.grid(row=6, column=0, columnspan=4, pady=10)

    # -------------------------
    # 翻牌
    # -------------------------
    def flip_card(self, index):

        if self.lock:
            return

        button = self.buttons[index]

        # 已翻開
        if button["text"] != "?":
            return

        # 顯示內容
        button["text"] = self.cards[index]
        button.update()

        # 第一張
        if self.first_card is None:
            self.first_card = index

        # 第二張
        else:
            self.second_card = index
            self.moves += 1

            self.move_label.config(text=f"步數: {self.moves}")

            self.check_match()

    # -------------------------
    # 檢查是否配對成功
    # -------------------------
    def check_match(self):

        first_idx = self.first_card
        second_idx = self.second_card

        first_symbol = self.cards[first_idx]
        second_symbol = self.cards[second_idx]

        # 配對成功
        if first_symbol == second_symbol:

            self.buttons[first_idx]["bg"] = "lightgreen"
            self.buttons[second_idx]["bg"] = "lightgreen"

            self.first_card = None
            self.second_card = None

            self.matched_pairs += 1

            # 全部完成
            if self.matched_pairs == len(self.symbols):
                messagebox.showinfo(
                    "恭喜",
                    f"你完成了遊戲！\n總步數：{self.moves}"
                )

        # 配對失敗
        else:
            self.lock = True

            self.root.after(1000, self.hide_cards)

    # -------------------------
    # 蓋牌
    # -------------------------
    def hide_cards(self):

        self.buttons[self.first_card]["text"] = "?"
        self.buttons[self.second_card]["text"] = "?"

        self.first_card = None
        self.second_card = None

        self.lock = False


# =========================
# 主程式
# =========================

if __name__ == "__main__":

    root = tk.Tk()
    game = MemoryGame(root)

    root.mainloop()