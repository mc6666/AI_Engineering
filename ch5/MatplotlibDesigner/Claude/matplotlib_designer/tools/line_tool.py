"""Tool that draws a new straight line by dragging from start to end."""
from __future__ import annotations

from typing import Optional, Tuple

from ..commands.add_shape import AddShapeCommand
from ..models.axes_model import AxesModel
from ..models.shape_model import ShapeModel
from .base_tool import BaseTool, ToolContext


class LineTool(BaseTool):
    """Click and drag inside an axes to draw a straight line segment."""

    name = "line"

    def __init__(self) -> None:
        """Initialize with no drag in progress."""
        self._axes: Optional[AxesModel] = None
        self._start: Tuple[float, float] = (0.0, 0.0)

    def on_press(self, ctx: ToolContext) -> None:
        """Record the line's start point."""
        if ctx.axes_model is None:
            return
        self._axes = ctx.axes_model
        self._start = (ctx.ax_x, ctx.ax_y)

    def on_move(self, ctx: ToolContext) -> None:
        """Update the live preview of the line being drawn."""
        if self._axes is None or ctx.ax_x is None:
            return
        x0, y0 = self._start
        ctx.canvas.set_preview_line(self._axes, x0, y0, ctx.ax_x, ctx.ax_y)

    def on_release(self, ctx: ToolContext) -> None:
        """Finalize the line and push an :class:`AddShapeCommand`."""
        canvas = ctx.canvas
        canvas.clear_preview()
        if self._axes is None or ctx.ax_x is None:
            self._axes = None
            return
        x0, y0 = self._start
        x1, y1 = ctx.ax_x, ctx.ax_y
        shape = ShapeModel(
            name="Line",
            kind="line",
            x=min(x0, x1),
            y=min(y0, y1),
            width=abs(x1 - x0),
            height=abs(y1 - y0),
            points=[(x0, y0), (x1, y1)],
        )
        command = AddShapeCommand(self._axes, shape, canvas.on_scene_changed)
        canvas.undo_manager.push(command)
        canvas.set_selection([shape])
        canvas.set_active_tool("select")
        self._axes = None
