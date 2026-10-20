"""Tool that zooms the data view of the axes under the cursor."""
from __future__ import annotations

from typing import Optional

from .base_tool import BaseTool, ToolContext

#: Zoom factor applied per click when no drag distance is registered.
CLICK_ZOOM_FACTOR = 0.7


class ZoomTool(BaseTool):
    """Click to zoom in; click-and-drag to zoom to a rectangle.

    Operates on the real Matplotlib data coordinates of the hovered axes
    (via ``ToolContext.mpl_event``), not on the design model, since zooming
    is a view convenience rather than a persisted design property.
    """

    name = "zoom"

    def __init__(self) -> None:
        """Initialize with no drag in progress."""
        self._ax = None
        self._start_data: Optional[tuple] = None

    def on_press(self, ctx: ToolContext) -> None:
        """Record the zoom rectangle's starting corner."""
        event = ctx.mpl_event
        if event is None or event.inaxes is None:
            return
        self._ax = event.inaxes
        self._start_data = (event.xdata, event.ydata)

    def on_release(self, ctx: ToolContext) -> None:
        """Apply a rectangle zoom, or a centered click-zoom for a plain click."""
        event = ctx.mpl_event
        if self._ax is None or event is None or event.inaxes is not self._ax:
            self._ax = None
            return
        x0, y0 = self._start_data
        x1, y1 = event.xdata, event.ydata
        if x1 is None or y1 is None:
            self._ax = None
            return
        if abs(x1 - x0) < 1e-9 and abs(y1 - y0) < 1e-9:
            xlim, ylim = self._ax.get_xlim(), self._ax.get_ylim()
            self._ax.set_xlim([x0 + (v - x0) * CLICK_ZOOM_FACTOR for v in xlim])
            self._ax.set_ylim([y0 + (v - y0) * CLICK_ZOOM_FACTOR for v in ylim])
        else:
            self._ax.set_xlim(sorted((x0, x1)))
            self._ax.set_ylim(sorted((y0, y1)))
        ctx.canvas.mpl_canvas.draw_idle()
        self._ax = None
