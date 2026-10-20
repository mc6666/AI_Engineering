#!/usr/bin/env python3
"""Safely evaluate numeric expressions for the calculator skill."""

from __future__ import annotations

import argparse
import ast
import math
import operator as op
import sys
from decimal import Decimal, getcontext
from fractions import Fraction


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

SAFE_FUNCS = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sqrt": math.sqrt,
    "floor": math.floor,
    "ceil": math.ceil,
    "trunc": math.trunc,
}

SAFE_CONSTS = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
}


class SafeEvaluator:
    def __init__(self, mode: str):
        self.mode = mode

    def evaluate(self, expression: str):
        tree = ast.parse(expression, mode="eval")
        return self._eval_node(tree.body)

    def _eval_node(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return self._convert_number(node.value)
            raise ValueError(f"Unsupported constant: {node.value!r}")
        if isinstance(node, ast.BinOp):
            operator = BIN_OPS.get(type(node.op))
            if operator is None:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return operator(left, right)
        if isinstance(node, ast.UnaryOp):
            operator = UNARY_OPS.get(type(node.op))
            if operator is None:
                raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
            return operator(self._eval_node(node.operand))
        if isinstance(node, ast.Name):
            if node.id not in SAFE_CONSTS:
                raise ValueError(f"Unknown name: {node.id}")
            return self._convert_number(SAFE_CONSTS[node.id])
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Only direct function calls are allowed")
            func_name = node.func.id
            func = SAFE_FUNCS.get(func_name)
            if func is None:
                raise ValueError(f"Unsupported function: {func_name}")
            args = [self._eval_node(arg) for arg in node.args]
            kwargs = {
                kw.arg: self._eval_node(kw.value)
                for kw in node.keywords
                if kw.arg is not None
            }
            if len(node.keywords) != len(kwargs):
                raise ValueError("Keyword unpacking is not allowed")
            return func(*args, **kwargs)
        raise ValueError(f"Unsupported expression element: {type(node).__name__}")

    def _convert_number(self, value):
        if self.mode == "fraction":
            if isinstance(value, int):
                return Fraction(value)
            return Fraction(str(value))
        if self.mode == "decimal":
            return Decimal(str(value))
        return value


def format_result(value):
    if isinstance(value, Decimal):
        normalized = value.normalize()
        rendered = format(normalized, "f")
        if "." in rendered:
            rendered = rendered.rstrip("0").rstrip(".")
        return rendered or "0"
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return repr(value)
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely evaluate a numeric expression.")
    parser.add_argument("expression", nargs="?", help="Expression to evaluate")
    parser.add_argument(
        "--mode",
        choices=("float", "fraction", "decimal"),
        default="float",
        help="Numeric mode to use for evaluation",
    )
    parser.add_argument(
        "--precision",
        type=int,
        default=28,
        help="Decimal precision when --mode decimal is selected",
    )
    args = parser.parse_args()

    expression = args.expression
    if expression is None:
        expression = sys.stdin.read().strip()
    if not expression:
        print("No expression provided.", file=sys.stderr)
        return 1

    if args.mode == "decimal":
        getcontext().prec = max(1, args.precision)

    evaluator = SafeEvaluator(args.mode)
    try:
        result = evaluator.evaluate(expression)
    except Exception as exc:  # Keep CLI errors explicit for skill use.
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(format_result(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
