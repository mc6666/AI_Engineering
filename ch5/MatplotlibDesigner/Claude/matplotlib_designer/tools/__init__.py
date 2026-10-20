"""Interactive canvas tools.

Each tool implements a small subset of mouse-event handlers
(:meth:`~matplotlib_designer.tools.base_tool.BaseTool.on_press`,
``on_move``, ``on_release``) and is responsible for creating exactly one
kind of scene object by dragging out a rectangle on the canvas (or, for the
text tool, a single click). The active tool is selected from the toolbar
and owned by :class:`matplotlib_designer.designer.canvas.SceneCanvas`.
"""

from .base_tool import BaseTool, ToolContext
from .select_tool import SelectTool
from .text_tool import TextTool
from .arrow_tool import ArrowTool
from .annotation_tool import AnnotationTool
from .rectangle_tool import RectangleTool
from .ellipse_tool import EllipseTool
from .line_tool import LineTool
from .zoom_tool import ZoomTool
from .pan_tool import PanTool

__all__ = [
    "BaseTool",
    "ToolContext",
    "SelectTool",
    "TextTool",
    "ArrowTool",
    "AnnotationTool",
    "RectangleTool",
    "EllipseTool",
    "LineTool",
    "ZoomTool",
    "PanTool",
]
