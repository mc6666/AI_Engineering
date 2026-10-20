"""Tool that pans the data view of the axes under the cursor by dragging."""
from __future__ import annotations

from typing import Optional, Tuple

from .base_tool import BaseTool, ToolContext


class PanTool(BaseTool):
    """Click and drag inside an axes to pan its data view (like grabbing paper).

    Operates on real Matplotlib data coordinates via ``ToolContext.mpl_event``.
    """

    name = "pan"

    def __init__(self) -> None:
        """Initialize with no drag in progress."""
        self._ax = None
        self._last_pixel: Optional[Tuple[float, float]] = None

    def on_press(self, ctx: ToolContext) -> None:
        """Begin panning from the current cursor position."""
        event = ctx.mpl_event
        if event is None or event.inaxes is None:
            return
        self._ax = event.inaxes
        self._last_pixel = (event.x, event.y)

    def on_move(self, ctx: ToolContext) -> None:
        """Shift the axes limits by the incremental data-space mouse delta."""
        event = ctx.mpl_event
        if self._ax is None or event is None or event.x is None:
            return
        inv = self._ax.transData.inverted()
        x0, y0 = inv.transform(self._last_pixel)
        x1, y1 = inv.transform((event.x, event.y))
        dx, dy = x1 - x0, y1 - y0
        xlim, ylim = self._ax.get_xlim(), self._ax.get_ylim()
        self._ax.set_xlim(xlim[0] - dx, xlim[1] - dx)
        self._ax.set_ylim(ylim[0] - dy, ylim[1] - dy)
        self._last_pixel = (event.x, event.y)
        ctx.canvas.mpl_canvas.draw_idle()

    def on_release(self, ctx: ToolContext) -> None:
        """End the panning gesture."""
        self._ax = None
        self._last_pixel = None
