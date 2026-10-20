import tkinter as tk
from tkinter import font as tkfont


# ── core logic (safe eval) ─────────────────────────────────────────────────────

def calculate(expression):
    try:
        allowed = set("0123456789+-*/(). %")
        if not all(c in allowed for c in expression):
            return None, "invalid characters"
        result = eval(expression)
        if isinstance(result, float):
            result = round(result, 10)
        return result, None
    except ZeroDivisionError:
        return None, "division by zero"
    except Exception:
        return None, "invalid expression"


# ── app ────────────────────────────────────────────────────────────────────────

BG       = "#0f0f0f"
SURFACE  = "#1a1a1a"
BORDER   = "#2a2a2a"
NUM_BG   = "#1e1e1e"
NUM_FG   = "#f0ede8"
OP_BG    = "#1e2a38"
OP_FG    = "#60a5fa"
EQ_BG    = "#1d4ed8"
EQ_FG    = "#ffffff"
CLR_FG   = "#f87171"
MUTED    = "#555555"
ERROR_FG = "#f87171"


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._expr = ""
        self._just_calc = False

        self._build_display()
        self._build_buttons()
        self._bind_keys()

    # ── display ──────────────────────────────────────────────────────────────

    def _build_display(self):
        frame = tk.Frame(self, bg=SURFACE, padx=20, pady=16)
        frame.pack(fill="x", padx=16, pady=(16, 8))

        self._expr_var = tk.StringVar(value="")
        self._res_var  = tk.StringVar(value="0")

        tk.Label(
            frame, textvariable=self._expr_var,
            bg=SURFACE, fg=MUTED,
            font=("Courier", 11), anchor="e",
            height=1
        ).pack(fill="x")

        self._res_label = tk.Label(
            frame, textvariable=self._res_var,
            bg=SURFACE, fg=NUM_FG,
            font=("Courier", 32, "bold"), anchor="e",
        )
        self._res_label.pack(fill="x")

    # ── buttons ───────────────────────────────────────────────────────────────

    def _build_buttons(self):
        frame = tk.Frame(self, bg=BG)
        frame.pack(padx=16, pady=(0, 16))

        layout = [
            [("AC", "clr"), ("⌫", "del"), ("%", "op"), ("÷", "op")],
            [("7",  "num"), ("8", "num"), ("9", "num"), ("×", "op")],
            [("4",  "num"), ("5", "num"), ("6", "num"), ("−", "op")],
            [("1",  "num"), ("2", "num"), ("3", "num"), ("+", "op")],
            [("0",  "num"), (".", "num"), ("=", "eq")],
        ]

        for r, row in enumerate(layout):
            for c, (label, kind) in enumerate(row):
                colspan = 2 if label == "0" else 1
                btn = self._make_btn(frame, label, kind)
                btn.grid(
                    row=r, column=c,
                    columnspan=colspan,
                    padx=4, pady=4,
                    sticky="nsew",
                    ipadx=10 if label == "0" else 0,
                )

        for i in range(4):
            frame.columnconfigure(i, weight=1, minsize=64)
        for i in range(5):
            frame.rowconfigure(i, weight=1, minsize=56)

    def _make_btn(self, parent, label, kind):
        bg = {"num": NUM_BG, "op": OP_BG, "eq": EQ_BG, "clr": NUM_BG, "del": NUM_BG}[kind]
        fg = {"num": NUM_FG, "op": OP_FG, "eq": EQ_FG, "clr": CLR_FG, "del": CLR_FG}[kind]

        btn = tk.Button(
            parent,
            text=label,
            bg=bg, fg=fg,
            activebackground=_lighten(bg),
            activeforeground=fg,
            font=("Courier", 16, "bold" if kind == "eq" else "normal"),
            relief="flat",
            bd=0,
            cursor="hand2",
            command=lambda l=label: self._on_press(l),
        )
        # hover effect
        btn.bind("<Enter>", lambda e, b=btn, c=_lighten(bg): b.config(bg=c))
        btn.bind("<Leave>", lambda e, b=btn, c=bg: b.config(bg=c))
        return btn

    # ── key bindings ──────────────────────────────────────────────────────────

    def _bind_keys(self):
        map_ = {
            "Return": "=", "KP_Enter": "=",
            "BackSpace": "⌫", "Escape": "AC",
            "slash": "÷", "asterisk": "×", "minus": "−",
        }
        for key, label in map_.items():
            self.bind(f"<{key}>", lambda e, l=label: self._on_press(l))
        for ch in "0123456789+-().%":
            self.bind(ch, lambda e, c=ch: self._on_press(c))

    # ── logic ─────────────────────────────────────────────────────────────────

    def _on_press(self, label):
        display_ops = {"÷": "/", "×": "*", "−": "-"}
        ops = set("+-*/÷×−%")

        if label == "AC":
            self._expr = ""
            self._just_calc = False
            self._set(result="0", expr="", error=False)
            return

        if label == "⌫":
            if self._just_calc:
                self._expr = ""
                self._just_calc = False
                self._set(result="0", expr="", error=False)
            else:
                self._expr = self._expr[:-1]
                self._set(result=self._display_expr(self._expr) or "0",
                          expr="", error=False)
            return

        if label == "=":
            if not self._expr:
                return
            val, err = calculate(self._expr)
            if err:
                self._set(result=f"Error: {err}", expr=self._display_expr(self._expr) + " =", error=True)
                self._expr = ""
            else:
                self._set(result=str(val),
                          expr=self._display_expr(self._expr) + " =", error=False)
                self._expr = str(val)
                self._just_calc = True
            return

        # regular input — just accumulate, no evaluation yet
        actual = display_ops.get(label, label)

        if self._just_calc and actual not in "+-*/÷×−%":
            self._expr = ""
        self._just_calc = False

        # prevent double operator
        if actual in "+-*/%" and self._expr and self._expr[-1] in "+-*/":
            self._expr = self._expr[:-1]

        # prevent double dot in same number segment
        if actual == "." and self._expr.split(actual)[-1].count(".") > 0:
            return

        self._expr += actual

        # show raw typed expression in result area; expr line stays empty
        self._set(result=self._display_expr(self._expr), expr="", error=False)

    def _display_expr(self, expr):
        return expr.replace("*", "×").replace("/", "÷").replace("-", "−")

    def _set(self, result, expr, error=False):
        self._res_var.set(result)
        self._expr_var.set(expr)
        self._res_label.config(fg=ERROR_FG if error else NUM_FG)

        # auto-shrink font for long results
        size = 32 if len(result) < 14 else 22 if len(result) < 20 else 16
        self._res_label.config(font=("Courier", size, "bold"))


def _lighten(hex_color, amount=20):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r = min(255, r + amount)
    g = min(255, g + amount)
    b = min(255, b + amount)
    return f"#{r:02x}{g:02x}{b:02x}"


if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
