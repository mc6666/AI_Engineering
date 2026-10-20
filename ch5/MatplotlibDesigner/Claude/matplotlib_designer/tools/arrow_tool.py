"""Tool that draws a plain arrow (no text callout) between two points."""
from __future__ import annotations

from typing import Optional, Tuple

from ..commands.add_arrow import AddAnnotationCommand
from ..models.annotation_model import AnnotationModel
from ..models.axes_model import AxesModel
from .base_tool import BaseTool, ToolContext


class ArrowTool(BaseTool):
    """Click and drag inside an axes to draw an arrow from tail to head.

    Implemented as an :class:`AnnotationModel` with an empty label and no
    box, so it reuses the same rendering, selection and serialization code
    as full annotations.
    """

    name = "arrow"

    def __init__(self) -> None:
        """Initialize with no drag in progress."""
        self._axes: Optional[AxesModel] = None
        self._start: Tuple[float, float] = (0.0, 0.0)

    def on_press(self, ctx: ToolContext) -> None:
        """Record the arrow's tail point."""
        if ctx.axes_model is None:
            return
        self._axes = ctx.axes_model
        self._start = (ctx.ax_x, ctx.ax_y)

    def on_move(self, ctx: ToolContext) -> None:
        """Update the live preview of the arrow being drawn."""
        if self._axes is None or ctx.ax_x is None:
            return
        x0, y0 = self._start
        ctx.canvas.set_preview_arrow(self._axes, x0, y0, ctx.ax_x, ctx.ax_y)

    def on_release(self, ctx: ToolContext) -> None:
        """Finalize the arrow and push an :class:`AddAnnotationCommand`."""
        canvas = ctx.canvas
        canvas.clear_preview()
        if self._axes is None or ctx.ax_x is None:
            self._axes = None
            return
        x0, y0 = self._start
        annotation = AnnotationModel(
            name="Arrow",
            text="",
            xtext=x0,
            ytext=y0,
            x=ctx.ax_x,
            y=ctx.ax_y,
            arrow_style="->",
            box_style="none",
        )
        command = AddAnnotationCommand(self._axes, annotation, canvas.on_scene_changed)
        canvas.undo_manager.push(command)
        canvas.set_selection([annotation])
        canvas.set_active_tool("select")
        self._axes = None
