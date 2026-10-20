import tkinter as tk
from tkinter import font as tkfont

# ── Color palette (bright mode) ────────────────────────────────────────────────
BG_WINDOW    = "#F5F4EF"
BG_CALC      = "#FFFFFF"
BG_DISPLAY   = "#FAFAF7"
BG_NUM       = "#F0EFE8"
BG_NUM_HOVER = "#E8E7DF"
BG_OP        = "#2D72D9"   # blue  – operators
BG_OP_ACT    = "#1A50AF"   # blue active (operator just pressed)
BG_EQ        = "#1DB954"   # green – equals
BG_DEL       = "#E84040"   # red   – AC / backspace

FG_NUM       = "#1A1A1A"
FG_WHITE     = "#FFFFFF"
FG_EXPR      = "#999999"
FG_RESULT    = "#1A1A1A"

BORDER_LIGHT = "#E2E0D8"
BORDER_NUM   = "#DDDBD2"

# ── Calculator logic ────────────────────────────────────────────────────────────
class Calculator:
    def __init__(self):
        self.input_str   = ""
        self.just_calced = False
        self.active_op   = None

    def _safe_eval(self, expr: str) -> str:
        try:
            result = eval(expr, {"__builtins__": {}})   # restricted eval
            if not isinstance(result, (int, float)) or not (result == result):
                return "Error"
            # trim float noise
            formatted = f"{result:.10g}"
            return formatted
        except Exception:
            return "Error"

    def press(self, val: str) -> tuple[str, str]:
        """Return (display_text, expr_text) after pressing a button."""
        ops = set("+-*/")

        if val == "AC":
            self.input_str   = ""
            self.just_calced = False
            self.active_op   = None
            return "0", ""

        if val == "DEL":
            if self.just_calced:
                self.input_str   = ""
                self.just_calced = False
                self.active_op   = None
                return "0", ""
            self.input_str = self.input_str[:-1]
            self.active_op = None
            return self.input_str or "0", ""

        if val == "=":
            if not self.input_str:
                return "0", ""
            expr_shown   = self.input_str + " ="
            result       = self._safe_eval(self.input_str)
            self.input_str   = "" if result == "Error" else result
            self.just_calced = True
            self.active_op   = None
            return result, expr_shown

        if val == "%":
            if self.input_str:
                self.input_str   = self._safe_eval(f"({self.input_str})/100")
                self.just_calced = False
                self.active_op   = None
            return self.input_str or "0", ""

        if val in ops:
            self.just_calced = False
            if not self.input_str and val == "-":
                self.input_str = "-"
                self.active_op = None
                return "-", ""
            if self.input_str:
                if self.input_str[-1] in ops:
                    self.input_str = self.input_str[:-1] + val
                else:
                    self.input_str += val
                self.active_op = val
                return self.input_str, self.input_str
            return self.input_str or "0", ""

        if val == ".":
            if self.just_calced:
                self.input_str   = "0."
                self.just_calced = False
                self.active_op   = None
                return "0.", ""
            parts = self.input_str.split("+") + self.input_str.split("-") + \
                    self.input_str.split("*") + self.input_str.split("/")
            # check last token for existing dot
            last = ""
            for ch in reversed(self.input_str):
                if ch in ops:
                    break
                last = ch + last
            if "." in last:
                return self.input_str or "0.", ""
            if not self.input_str or self.input_str[-1] in ops:
                self.input_str += "0"
            self.input_str += "."
            self.active_op  = None
            return self.input_str, ""

        # digit
        if self.just_calced:
            self.input_str   = ""
            self.just_calced = False
            self.active_op   = None
        self.input_str += val
        self.active_op  = None
        return self.input_str, ""


# ── GUI ─────────────────────────────────────────────────────────────────────────
class CalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.resizable(False, False)
        self.configure(bg=BG_WINDOW)

        self.logic       = Calculator()
        self._btn_refs   = {}   # val -> Button widget
        self._after_ids  = {}   # val -> after-id for press animation

        self._build_ui()
        self._bind_keys()

    # ── Build UI ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        pad = dict(padx=16, pady=16)

        outer = tk.Frame(self, bg=BG_WINDOW)
        outer.pack(**pad)

        calc = tk.Frame(outer, bg=BG_CALC, bd=0, highlightthickness=1,
                        highlightbackground=BORDER_LIGHT)
        calc.pack(padx=0, pady=0)

        # display
        disp_frame = tk.Frame(calc, bg=BG_DISPLAY, bd=0, highlightthickness=1,
                              highlightbackground=BORDER_LIGHT)
        disp_frame.pack(fill="x", padx=16, pady=(16, 8))

        self.expr_var   = tk.StringVar(value="")
        self.result_var = tk.StringVar(value="0")

        self.expr_lbl = tk.Label(disp_frame, textvariable=self.expr_var,
                                 font=("Courier", 11), fg=FG_EXPR, bg=BG_DISPLAY,
                                 anchor="e", justify="right")
        self.expr_lbl.pack(fill="x", padx=10, pady=(8, 0))

        self.result_lbl = tk.Label(disp_frame, textvariable=self.result_var,
                                   font=("Courier", 28, "bold"), fg=FG_RESULT,
                                   bg=BG_DISPLAY, anchor="e", justify="right")
        self.result_lbl.pack(fill="x", padx=10, pady=(0, 10))

        # button grid
        btn_frame = tk.Frame(calc, bg=BG_CALC)
        btn_frame.pack(padx=12, pady=(0, 16))

        layout = [
            [("AC", "del"), ("⌫", "del"), ("%", "op"),  ("÷", "op")],
            [("7",  "num"), ("8",  "num"), ("9", "num"), ("×", "op")],
            [("4",  "num"), ("5",  "num"), ("6", "num"), ("−", "op")],
            [("1",  "num"), ("2",  "num"), ("3", "num"), ("+", "op")],
            [("0",  "num", 2), (".", "num"), ("=", "eq")],
        ]

        for r, row in enumerate(layout):
            c = 0
            for item in row:
                label    = item[0]
                kind     = item[1]
                colspan  = item[2] if len(item) > 2 else 1
                internal = {"÷": "/", "×": "*", "−": "-", "⌫": "DEL"}.get(label, label)

                bg, fg = self._colors(kind)
                btn = tk.Button(
                    btn_frame,
                    text=label,
                    font=("Helvetica", 16, "bold"),
                    bg=bg, fg=fg,
                    activebackground=bg,
                    activeforeground=fg,
                    relief="flat",
                    bd=0,
                    cursor="hand2",
                    width=4 * colspan,
                    height=2,
                    command=lambda v=internal: self._on_press(v),
                )
                btn.grid(row=r, column=c, columnspan=colspan,
                         padx=4, pady=4, sticky="nsew")
                self._btn_refs[internal] = btn

                # hover effect for num buttons
                if kind == "num":
                    btn.bind("<Enter>", lambda e, b=btn: b.config(bg=BG_NUM_HOVER))
                    btn.bind("<Leave>", lambda e, b=btn, bg_=bg: b.config(bg=bg_))

                c += colspan

    def _colors(self, kind):
        if kind == "op":  return BG_OP,  FG_WHITE
        if kind == "eq":  return BG_EQ,  FG_WHITE
        if kind == "del": return BG_DEL, FG_WHITE
        return BG_NUM, FG_NUM

    # ── Logic bridge ────────────────────────────────────────────────────────────
    def _on_press(self, val: str):
        display, expr = self.logic.press(val)
        self._update_display(display, expr)
        self._highlight_op()
        self._flash_btn(val)

    def _update_display(self, display: str, expr: str):
        self.result_var.set(display)
        self.expr_var.set(expr)
        # shrink font for long numbers
        size = 28
        if len(display) > 14: size = 14
        elif len(display) > 10: size = 18
        elif len(display) > 7:  size = 22
        self.result_lbl.config(font=("Courier", size, "bold"))

    def _highlight_op(self):
        for val, btn in self._btn_refs.items():
            if val in "+-*/" :
                active = (val == self.logic.active_op)
                btn.config(bg=BG_OP_ACT if active else BG_OP)

    def _flash_btn(self, val: str):
        btn = self._btn_refs.get(val)
        if not btn:
            return
        orig_bg = btn.cget("bg")
        btn.config(bg=self._darken(orig_bg))
        if val in self._after_ids:
            self.after_cancel(self._after_ids[val])
        self._after_ids[val] = self.after(120, lambda b=btn, c=orig_bg: b.config(bg=c))

    def _darken(self, hex_color: str) -> str:
        hex_color = hex_color.lstrip("#")
        r, g, b   = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b   = max(0, r-30), max(0, g-30), max(0, b-30)
        return f"#{r:02x}{g:02x}{b:02x}"

    # ── Keyboard bindings ───────────────────────────────────────────────────────
    def _bind_keys(self):
        key_map = {
            "0": "0", "1": "1", "2": "2", "3": "3", "4": "4",
            "5": "5", "6": "6", "7": "7", "8": "8", "9": "9",
            "plus": "+", "minus": "-", "asterisk": "*", "slash": "/",
            "period": ".", "percent": "%",
            "Return": "=", "equal": "=",
            "BackSpace": "DEL",
            "Escape": "AC", "Delete": "AC",
        }
        for key, val in key_map.items():
            self.bind(f"<KeyPress-{key}>", lambda e, v=val: self._on_press(v))


# ── Entry point ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = CalculatorApp()
    app.mainloop()
