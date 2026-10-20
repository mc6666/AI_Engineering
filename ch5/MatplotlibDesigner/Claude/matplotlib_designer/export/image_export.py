"""Raster/vector image export (PNG, PDF, SVG, EPS, JPG, TIFF)."""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

#: Matplotlib ``savefig`` format keyword for each supported extension.
SUPPORTED_FORMATS = {"png", "pdf", "svg", "eps", "jpg", "jpeg", "tiff"}


def export_image(canvas, path: Union[str, Path], fmt: Optional[str] = None) -> None:
    """Export the canvas's current figure to an image/vector file.

    The selection overlay (handles, rubber band, previews) is hidden for
    the duration of the export so it never appears in the saved output.

    Args:
        canvas: The :class:`~matplotlib_designer.designer.canvas.SceneCanvas`
            whose live Matplotlib figure will be saved.
        path: Destination file path.
        fmt: Explicit format (``"png"``, ``"pdf"``, ``"svg"``, ``"eps"``,
            ``"jpg"``, ``"tiff"``); inferred from ``path``'s suffix if omitted.

    Raises:
        ValueError: If the format is not supported.
    """
    fmt = (fmt or Path(path).suffix.lstrip(".")).lower()
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported export format: {fmt}")

    figure = canvas.figure
    overlay = getattr(canvas, "_overlay_ax", None)
    was_visible = overlay.get_visible() if overlay is not None else False
    if overlay is not None:
        overlay.set_visible(False)
    try:
        figure.savefig(path, format=fmt, dpi=figure.dpi, facecolor=figure.get_facecolor())
    finally:
        if overlay is not None:
            overlay.set_visible(was_visible)
        canvas.mpl_canvas.draw_idle()
