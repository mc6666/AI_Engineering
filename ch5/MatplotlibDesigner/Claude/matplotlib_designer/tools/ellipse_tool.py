"""Tool that draws a new ellipse shape by dragging out its bounds."""
from __future__ import annotations

from .rectangle_tool import RectangleTool


class EllipseTool(RectangleTool):
    """Click and drag inside an axes to draw an ellipse.

    Reuses all of :class:`RectangleTool`'s drag/preview/commit logic; only
    the produced :class:`~matplotlib_designer.models.shape_model.ShapeModel`
    kind differs.
    """

    name = "ellipse"
    shape_kind = "ellipse"
