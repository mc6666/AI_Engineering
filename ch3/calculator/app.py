from __future__ import annotations

import ast
import operator as op
import tkinter as tk
from tkinter import ttk


class SafeEvaluator(ast.NodeVisitor):
    """Evaluate a small arithmetic expression safely."""

    BIN_OPS = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Div: op.truediv,
        ast.FloorDiv: op.floordiv,
        ast.Mod: op.mod,
        ast.Pow: op.pow,
    }

    UNARY_OPS = {
        ast.UAdd: op.pos,
        ast.USub: op.neg,
    }

    def visit_Expression(self, node: ast.Expression):
        return self.visit(node.body)

    def visit_BinOp(self, node: ast.BinOp):
        left = self.visit(node.left)
        right = self.visit(node.right)
        operator = self.BIN_OPS.get(type(node.op))
        if operator is None:
            raise ValueError("Unsupported operator")
        return operator(left, right)

    def visit_UnaryOp(self, node: ast.UnaryOp):
        operand = self.visit(node.operand)
        operator = self.UNARY_OPS.get(type(node.op))
        if operator is None:
            raise ValueError("Unsupported operator")
        return operator(operand)

    def visit_Constant(self, node: ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric constants are allowed")

    def visit_Num(self, node: ast.Num):  # pragma: no cover - compatibility
        return node.n

    def generic_visit(self, node):
        raise ValueError(f"Unsupported expression: {type(node).__name__}")


def safe_eval(expression: str):
    tree = ast.parse(expression, mode="eval")
    return SafeEvaluator().visit(tree)


class CalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter Calculator")
        self.resizable(False, False)
        self.configure(padx=14, pady=14)

        self.expression = tk.StringVar(value="")
        self.result = tk.StringVar(value="0")

        self._build_ui()
        self._bind_keys()

    def _build_ui(self):
        display = ttk.Frame(self)
        display.grid(row=0, column=0, sticky="ew")
        display.columnconfigure(0, weight=1)

        entry = ttk.Entry(
            display,
            textvariable=self.expression,
            font=("Segoe UI", 18),
            justify="right",
            state="readonly",
            width=18,
        )
        entry.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        result_label = ttk.Label(
            display,
            textvariable=self.result,
            font=("Segoe UI", 12),
            anchor="e",
        )
        result_label.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        keypad = ttk.Frame(self)
        keypad.grid(row=1, column=0)

        buttons = [
            ("C", self.clear),
            ("DEL", self.backspace),
            ("%", lambda: self.append("%")),
            ("/", lambda: self.append("/")),
            ("7", lambda: self.append("7")),
            ("8", lambda: self.append("8")),
            ("9", lambda: self.append("9")),
            ("*", lambda: self.append("*")),
            ("4", lambda: self.append("4")),
            ("5", lambda: self.append("5")),
            ("6", lambda: self.append("6")),
            ("-", lambda: self.append("-")),
            ("1", lambda: self.append("1")),
            ("2", lambda: self.append("2")),
            ("3", lambda: self.append("3")),
            ("+", lambda: self.append("+")),
            ("0", lambda: self.append("0")),
            (".", lambda: self.append(".")),
            ("(", lambda: self.append("(")),
            (")", lambda: self.append(")")),
            ("=", self.calculate),
        ]

        for index, (text, command) in enumerate(buttons):
            row, col = divmod(index, 4)
            colspan = 2 if text == "=" else 1
            width = 16 if text == "=" else 6
            btn = ttk.Button(keypad, text=text, command=command, width=width)
            btn.grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=3, pady=3)

        for col in range(4):
            keypad.columnconfigure(col, weight=1)

        for row in range(6):
            keypad.rowconfigure(row, weight=1)

        keypad.columnconfigure(1, weight=1)
        keypad.columnconfigure(2, weight=1)
        keypad.columnconfigure(3, weight=1)

    def _bind_keys(self):
        self.bind_all("<Return>", lambda _: self.calculate())
        self.bind_all("<KP_Enter>", lambda _: self.calculate())
        self.bind_all("<Escape>", lambda _: self.clear())
        self.bind_all("<BackSpace>", lambda _: self.backspace())

        for char in "0123456789+-*/().%":
            self.bind_all(char, lambda event, c=char: self.append(c))

    def append(self, text: str):
        self.expression.set(self.expression.get() + text)
        self.result.set("")

    def clear(self):
        self.expression.set("")
        self.result.set("0")

    def backspace(self):
        current = self.expression.get()
        self.expression.set(current[:-1])

    def calculate(self):
        expr = self.expression.get().strip()
        if not expr:
            self.result.set("0")
            return

        try:
            value = safe_eval(expr)
        except Exception:
            self.result.set("Error")
            return

        if isinstance(value, float) and value.is_integer():
            value = int(value)
        self.result.set(str(value))


def main():
    app = CalculatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
