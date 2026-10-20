"""Pickle export: save the live Matplotlib figure object as-is."""
from __future__ import annotations

import pickle
from pathlib import Path
from typing import Union


def export_pickle(canvas, path: Union[str, Path]) -> None:
    """Pickle the canvas's current Matplotlib figure to disk.

    The selection overlay is hidden (but not removed) before pickling so a
    later ``pickle.load`` reproduces exactly what the user designed.

    Args:
        canvas: The :class:`~matplotlib_designer.designer.canvas.SceneCanvas`.
        path: Destination ``.pickle``/``.pkl`` file path.
    """
    overlay = getattr(canvas, "_overlay_ax", None)
    was_visible = overlay.get_visible() if overlay is not None else False
    if overlay is not None:
        overlay.set_visible(False)
    try:
        with open(path, "wb") as handle:
            pickle.dump(canvas.figure, handle)
    finally:
        if overlay is not None:
            overlay.set_visible(was_visible)
