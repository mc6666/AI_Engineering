---
name: calculator
description: Compute arithmetic, percentages, units, and other numeric expressions with Python. Use when Codex needs to evaluate formulas, verify calculations, compare values, or produce exact numeric results.
---

# Calculator

## Overview

Use this skill for arithmetic that benefits from exact, repeatable computation in Python.

## Workflow

1. Translate the user request into a precise expression or small set of expressions.
1. Use the Python helper in `scripts/calculate.py` for evaluation when the result should be exact or reproducible.
1. Prefer rational arithmetic when fractions matter.
1. Use `decimal.Decimal` when the user needs controlled precision.
1. Report the result with the original units and a short breakdown only when it adds clarity.

## Supported Inputs

- Basic arithmetic: `+`, `-`, `*`, `/`, `//`, `%`, `**`
- Parentheses and unary plus/minus
- Common numeric helpers such as `abs`, `round`, `min`, `max`, `sqrt`, `floor`, and `ceil`
- Constants: `pi`, `e`, `tau`

## Usage Notes

- Reject or normalize ambiguous wording before calculating.
- Keep intermediate steps simple and explicit for multi-step problems.
- If the user asks for a result in a particular format, match that format exactly.
- If an expression cannot be represented safely, explain the limitation instead of improvising with `eval`.

## Script

`scripts/calculate.py` evaluates a single expression safely from the command line or stdin.
