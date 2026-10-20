"""Tool that places a new free text object with a single click."""
from __future__ import annotations

from ..commands.add_text import AddTextCommand
from ..models.text_model import TextModel
from .base_tool import BaseTool, ToolContext


class TextTool(BaseTool):
    """Click anywhere inside an axes to drop a new editable text object."""

    name = "text"

    def on_press(self, ctx: ToolContext) -> None:
        """Create a text object at the click position and select it."""
        if ctx.axes_model is None:
            return
        canvas = ctx.canvas
        text = TextModel(name="Text", content="Text", x=ctx.ax_x, y=ctx.ax_y)
        command = AddTextCommand(ctx.axes_model, text, canvas.on_scene_changed)
        canvas.undo_manager.push(command)
        canvas.set_selection([text])
        canvas.set_active_tool("select")
        canvas.request_inline_edit(text)
