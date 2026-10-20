"""Tool that draws a full annotation: leader arrow plus a text callout box."""
from __future__ import annotations

from typing import Optional, Tuple

from ..commands.add_arrow import AddAnnotationCommand
from ..models.annotation_model import AnnotationModel
from ..models.axes_model import AxesModel
from .base_tool import BaseTool, ToolContext


class AnnotationTool(BaseTool):
    """Click the point of interest, drag to where the label should sit."""

    name = "annotation"

    def __init__(self) -> None:
        """Initialize with no drag in progress."""
        self._axes: Optional[AxesModel] = None
        self._start: Tuple[float, float] = (0.0, 0.0)

    def on_press(self, ctx: ToolContext) -> None:
        """Record the anchor point being annotated."""
        if ctx.axes_model is None:
            return
        self._axes = ctx.axes_model
        self._start = (ctx.ax_x, ctx.ax_y)

    def on_move(self, ctx: ToolContext) -> None:
        """Update the live preview of the callout being drawn."""
        if self._axes is None or ctx.ax_x is None:
            return
        x0, y0 = self._start
        ctx.canvas.set_preview_arrow(self._axes, x0, y0, ctx.ax_x, ctx.ax_y)

    def on_release(self, ctx: ToolContext) -> None:
        """Finalize the annotation and push an :class:`AddAnnotationCommand`."""
        canvas = ctx.canvas
        canvas.clear_preview()
        if self._axes is None or ctx.ax_x is None:
            self._axes = None
            return
        x0, y0 = self._start
        annotation = AnnotationModel(
            name="Annotation",
            text="Annotation",
            x=x0,
            y=y0,
            xtext=ctx.ax_x,
            ytext=ctx.ax_y,
            arrow_style="->",
            box_style="round",
        )
        command = AddAnnotationCommand(self._axes, annotation, canvas.on_scene_changed)
        canvas.undo_manager.push(command)
        canvas.set_selection([annotation])
        canvas.set_active_tool("select")
        canvas.request_inline_edit(annotation)
        self._axes = None
