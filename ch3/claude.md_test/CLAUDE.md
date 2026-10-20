# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```
python calculator.py
```

Requires Python 3 with `tkinter` (included in standard CPython distributions on Windows).

## Project Structure

A single-file tkinter GUI calculator (`calculator.py`). All UI construction, button layout, and event logic live in one module-level script — no classes, no imports beyond `tkinter`.

State is managed via two globals:
- `expression` — accumulates the input string
- `equation` — `tk.StringVar` bound to the entry widget

## Spec vs. Current Implementation

`calculator_spec.txt` defines the intended feature set. The current `calculator.py` is a baseline that does **not** yet implement:

- Keyboard bindings (numbers, `+`, `-`, `*`, `/`, `Enter`, `Backspace`, `Esc`)
- Color-coded buttons (blue = operators, red = clear/delete, green = `=`)
- Deferred display (no live preview — expression stays hidden until `=` is pressed)
- Bright mode UI theme

When modifying the calculator, use `calculator_spec.txt` as the authoritative requirements source.

## Assets

`assets/` contains PNG sprites and a BGM audio file. These are not referenced by the current `calculator.py` — they appear intended for a future enhanced UI version.
