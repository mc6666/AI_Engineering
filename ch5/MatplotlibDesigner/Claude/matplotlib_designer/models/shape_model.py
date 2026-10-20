"""Model for vector shapes: rectangles, ellipses, circles, lines, polygons."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from .base_model import SceneObject


@dataclass
class ShapeModel(SceneObject):
    """A vector shape drawn on top of an axes.

    Position and size are expressed in axes-fraction coordinates so shapes
    remain correctly placed if the axes is resized.

    Attributes:
        kind: One of ``"rectangle"``, ``"ellipse"``, ``"circle"``,
            ``"line"``, ``"polygon"``, ``"bezier"``, ``"freehand"``.
        x: Left (or center, for circle/ellipse) x position.
        y: Bottom (or center) y position.
        width: Bounding box width.
        height: Bounding box height.
        points: Vertex list used by ``line``, ``polygon``, ``bezier`` and
            ``freehand`` kinds, as ``(x, y)`` tuples in axes-fraction
            coordinates.
        edge_color: Outline color.
        face_color: Fill color.
        line_width: Outline width in points.
        line_style: Matplotlib line style code (e.g. ``"-"``, ``"--"``).
        rotation: Rotation angle in degrees, about the shape center.
    """

    kind: str = "rectangle"
    x: float = 0.3
    y: float = 0.3
    width: float = 0.2
    height: float = 0.2
    points: List[Tuple[float, float]] = field(default_factory=list)
    edge_color: str = "#333333"
    face_color: str = "#3078c8"
    line_width: float = 1.5
    line_style: str = "-"
    rotation: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize this shape, including base attributes."""
        data = super().to_dict()
        data.update(
            type="shape",
            kind=self.kind,
            x=self.x,
            y=self.y,
            width=self.width,
            height=self.height,
            points=[list(p) for p in self.points],
            edge_color=self.edge_color,
            face_color=self.face_color,
            line_width=self.line_width,
            line_style=self.line_style,
            rotation=self.rotation,
        )
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShapeModel":
        """Reconstruct a :class:`ShapeModel` from serialized data."""
        obj = cls(
            kind=data.get("kind", "rectangle"),
            x=data.get("x", 0.3),
            y=data.get("y", 0.3),
            width=data.get("width", 0.2),
            height=data.get("height", 0.2),
            points=[tuple(p) for p in data.get("points", [])],
            edge_color=data.get("edge_color", "#333333"),
            face_color=data.get("face_color", "#3078c8"),
            line_width=data.get("line_width", 1.5),
            line_style=data.get("line_style", "-"),
            rotation=data.get("rotation", 0.0),
        )
        obj.apply_base(data)
        return obj
