import tkinter as tk
from tkinter import font
import math


class ScientificCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Scientific Calculator")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(False, False)

        self.expression = ""
        self.display_var = tk.StringVar(value="0")
        self.history_var = tk.StringVar(value="")
        self.angle_mode = "DEG"  # DEG or RAD
        self.memory = 0.0

        self._build_ui()

    # ------------------------------------------------------------------ UI --

    def _build_ui(self):
        # ── top bar (angle mode + memory indicator) ──────────────────────
        top_bar = tk.Frame(self.root, bg="#1e1e2e")
        top_bar.pack(fill="x", padx=8, pady=(8, 0))

        self.mode_btn = tk.Button(
            top_bar, text="DEG", width=5, font=("Consolas", 10, "bold"),
            bg="#313244", fg="#cba6f7", activebackground="#45475a",
            activeforeground="#cba6f7", relief="flat", cursor="hand2",
            command=self.toggle_angle_mode
        )
        self.mode_btn.pack(side="left")

        self.mem_label = tk.Label(
            top_bar, text="", font=("Consolas", 10), bg="#1e1e2e", fg="#f38ba8"
        )
        self.mem_label.pack(side="right")

        # ── history / expression strip ────────────────────────────────────
        tk.Label(
            self.root, textvariable=self.history_var,
            font=("Consolas", 11), bg="#1e1e2e", fg="#585b70",
            anchor="e", padx=12
        ).pack(fill="x")

        # ── main display ──────────────────────────────────────────────────
        tk.Label(
            self.root, textvariable=self.display_var,
            font=("Consolas", 32, "bold"), bg="#1e1e2e", fg="#cdd6f4",
            anchor="e", padx=12, pady=4
        ).pack(fill="x")

        tk.Frame(self.root, bg="#313244", height=1).pack(fill="x", padx=8)

        # ── button grid ───────────────────────────────────────────────────
        btn_frame = tk.Frame(self.root, bg="#1e1e2e", padx=8, pady=8)
        btn_frame.pack()

        # (label, column, row, colspan, color_key, command)
        buttons = [
            # Row 0 – memory
            ("MC",  0, 0, 1, "mem",  lambda: self.memory_clear()),
            ("MR",  1, 0, 1, "mem",  lambda: self.memory_recall()),
            ("M+",  2, 0, 1, "mem",  lambda: self.memory_add()),
            ("M−",  3, 0, 1, "mem",  lambda: self.memory_sub()),
            ("MS",  4, 0, 1, "mem",  lambda: self.memory_store()),

            # Row 1 – scientific A
            ("sin", 0, 1, 1, "sci",  lambda: self.trig("sin")),
            ("cos", 1, 1, 1, "sci",  lambda: self.trig("cos")),
            ("tan", 2, 1, 1, "sci",  lambda: self.trig("tan")),
            ("π",   3, 1, 1, "sci",  lambda: self.insert_const(math.pi)),
            ("e",   4, 1, 1, "sci",  lambda: self.insert_const(math.e)),

            # Row 2 – scientific B
            ("x²",  0, 2, 1, "sci",  lambda: self.power(2)),
            ("x³",  1, 2, 1, "sci",  lambda: self.power(3)),
            ("xʸ",  2, 2, 1, "sci",  lambda: self.append("**")),
            ("√",   3, 2, 1, "sci",  lambda: self.unary(math.sqrt)),
            ("∛",   4, 2, 1, "sci",  lambda: self.unary(lambda x: x ** (1/3))),

            # Row 3 – scientific C
            ("log", 0, 3, 1, "sci",  lambda: self.unary(math.log10)),
            ("ln",  1, 3, 1, "sci",  lambda: self.unary(math.log)),
            ("1/x", 2, 3, 1, "sci",  lambda: self.unary(lambda x: 1/x)),
            ("|x|", 3, 3, 1, "sci",  lambda: self.unary(abs)),
            ("n!",  4, 3, 1, "sci",  lambda: self.factorial()),

            # Row 4 – brackets + percent + clear
            ("(",   0, 4, 1, "op",   lambda: self.append("(")),
            (")",   1, 4, 1, "op",   lambda: self.append(")")),
            ("%",   2, 4, 1, "op",   lambda: self.percent()),
            ("CE",  3, 4, 1, "clear",lambda: self.clear_entry()),
            ("C",   4, 4, 1, "clear",lambda: self.clear_all()),

            # Row 5
            ("7",   0, 5, 1, "num",  lambda: self.append("7")),
            ("8",   1, 5, 1, "num",  lambda: self.append("8")),
            ("9",   2, 5, 1, "num",  lambda: self.append("9")),
            ("⌫",   3, 5, 1, "clear",lambda: self.backspace()),
            ("÷",   4, 5, 1, "op",   lambda: self.append("/")),

            # Row 6
            ("4",   0, 6, 1, "num",  lambda: self.append("4")),
            ("5",   1, 6, 1, "num",  lambda: self.append("5")),
            ("6",   2, 6, 1, "num",  lambda: self.append("6")),
            ("×",   3, 6, 1, "op",   lambda: self.append("*")),
            ("−",   4, 6, 1, "op",   lambda: self.append("-")),

            # Row 7
            ("1",   0, 7, 1, "num",  lambda: self.append("1")),
            ("2",   1, 7, 1, "num",  lambda: self.append("2")),
            ("3",   2, 7, 1, "num",  lambda: self.append("3")),
            ("+",   3, 7, 1, "op",   lambda: self.append("+")),
            ("=",   4, 7, 1, "eq",   lambda: self.evaluate()),

            # Row 8
            ("±",   0, 8, 1, "op",   lambda: self.negate()),
            ("0",   1, 8, 1, "num",  lambda: self.append("0")),
            (".",   2, 8, 1, "num",  lambda: self.append(".")),
            ("EXP", 3, 8, 1, "sci",  lambda: self.append("e")),
        ]

        colors = {
            "num":   ("#313244", "#cdd6f4"),
            "op":    ("#45475a", "#89b4fa"),
            "sci":   ("#181825", "#a6e3a1"),
            "mem":   ("#181825", "#f9e2af"),
            "clear": ("#45475a", "#f38ba8"),
            "eq":    ("#89b4fa", "#1e1e2e"),
        }
        hover = {
            "num":   "#45475a",
            "op":    "#585b70",
            "sci":   "#313244",
            "mem":   "#313244",
            "clear": "#585b70",
            "eq":    "#74c7ec",
        }

        for (label, col, row, cs, ck, cmd) in buttons:
            bg, fg = colors[ck]
            hv = hover[ck]
            b = tk.Button(
                btn_frame, text=label,
                font=("Consolas", 13, "bold"),
                bg=bg, fg=fg,
                activebackground=hv, activeforeground=fg,
                relief="flat", cursor="hand2",
                width=5, height=2,
                command=cmd
            )
            b.grid(row=row, column=col, columnspan=cs,
                   padx=3, pady=3, sticky="nsew")

        # keyboard bindings
        self.root.bind("<Key>", self.key_press)
        self.root.bind("<Return>", lambda e: self.evaluate())
        self.root.bind("<BackSpace>", lambda e: self.backspace())
        self.root.bind("<Escape>", lambda e: self.clear_all())

    # ----------------------------------------------------------- helpers ---

    def _update_display(self, value):
        text = str(value)
        # trim long floats
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        if len(text) > 16:
            text = f"{float(text):.6e}"
        self.display_var.set(text if text else "0")

    def _to_rad(self, deg):
        return deg * math.pi / 180 if self.angle_mode == "DEG" else deg

    def _current_num(self):
        try:
            return float(self.display_var.get())
        except ValueError:
            return None

    # ----------------------------------------------------------- actions ---

    def append(self, char):
        if self.display_var.get() == "Error":
            self.expression = ""
        if self.display_var.get() == "0" and char not in ".+-*/(**":
            self.expression = ""
        self.expression += char
        self.display_var.set(self.expression)

    def clear_all(self):
        self.expression = ""
        self.display_var.set("0")
        self.history_var.set("")

    def clear_entry(self):
        self.expression = ""
        self.display_var.set("0")

    def backspace(self):
        self.expression = self.expression[:-1]
        self.display_var.set(self.expression if self.expression else "0")

    def evaluate(self):
        if not self.expression:
            return
        try:
            self.history_var.set(self.expression + " =")
            result = eval(self.expression, {"__builtins__": {}}, {})
            self._update_display(result)
            self.expression = str(result)
        except ZeroDivisionError:
            self.display_var.set("Div/0 Error")
            self.expression = ""
        except Exception:
            self.display_var.set("Error")
            self.expression = ""

    def trig(self, fn):
        val = self._current_num()
        if val is None:
            return
        rad = self._to_rad(val)
        try:
            result = getattr(math, fn)(rad)
            # round near-zero values (e.g. sin(180°))
            if abs(result) < 1e-12:
                result = 0.0
            self._update_display(result)
            self.expression = str(result)
        except Exception:
            self.display_var.set("Error")
            self.expression = ""

    def unary(self, func):
        val = self._current_num()
        if val is None:
            return
        try:
            result = func(val)
            self._update_display(result)
            self.expression = str(result)
        except Exception:
            self.display_var.set("Error")
            self.expression = ""

    def power(self, exp):
        val = self._current_num()
        if val is None:
            return
        result = val ** exp
        self._update_display(result)
        self.expression = str(result)

    def factorial(self):
        val = self._current_num()
        if val is None or val < 0 or val != int(val):
            self.display_var.set("Error")
            self.expression = ""
            return
        result = math.factorial(int(val))
        self._update_display(result)
        self.expression = str(result)

    def percent(self):
        val = self._current_num()
        if val is None:
            return
        result = val / 100
        self._update_display(result)
        self.expression = str(result)

    def negate(self):
        val = self._current_num()
        if val is None:
            return
        result = -val
        self._update_display(result)
        self.expression = str(result)

    def insert_const(self, value):
        self.expression += str(value)
        self.display_var.set(self.expression)

    def toggle_angle_mode(self):
        self.angle_mode = "RAD" if self.angle_mode == "DEG" else "DEG"
        self.mode_btn.config(text=self.angle_mode)

    # ----------------------------------------------------------- memory ---

    def memory_store(self):
        val = self._current_num()
        if val is not None:
            self.memory = val
            self.mem_label.config(text="M")

    def memory_recall(self):
        self.expression = str(self.memory)
        self._update_display(self.memory)

    def memory_add(self):
        val = self._current_num()
        if val is not None:
            self.memory += val
            self.mem_label.config(text="M")

    def memory_sub(self):
        val = self._current_num()
        if val is not None:
            self.memory -= val
            self.mem_label.config(text="M")

    def memory_clear(self):
        self.memory = 0.0
        self.mem_label.config(text="")

    # ---------------------------------------------------------- keyboard --

    def key_press(self, event):
        key = event.char
        if key in "0123456789.+-*/()":
            self.append(key)
        elif key == "p":
            self.insert_const(math.pi)
        elif key == "e":
            self.insert_const(math.e)
        elif key == "s":
            self.trig("sin")
        elif key == "c":
            self.trig("cos")
        elif key == "t":
            self.trig("tan")
        elif key == "l":
            self.unary(math.log10)
        elif key == "n":
            self.unary(math.log)
        elif key == "q":
            self.unary(math.sqrt)
        elif key == "%":
            self.percent()


if __name__ == "__main__":
    root = tk.Tk()
    app = ScientificCalculator(root)
    root.mainloop()
