"""Model for annotations: arrow + text callouts with optional boxes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .base_model import SceneObject


@dataclass
class AnnotationModel(SceneObject):
    """A text callout connected to a point of interest by a leader/arrow.

    Coordinates are in axes-fraction space.

    Attributes:
        text: The annotation label text.
        x: X position of the point being annotated (arrow tip).
        y: Y position of the point being annotated (arrow tip).
        xtext: X position of the text box.
        ytext: Y position of the text box.
        arrow_style: Matplotlib ``arrowstyle`` code, e.g. ``"->"``, ``"-|>"``.
            Empty string means no arrow/leader line is drawn.
        box_style: Matplotlib ``boxstyle`` code, e.g. ``"round"``, ``"square"``,
            or ``"none"`` for no box.
        face_color: Callout box fill color.
        edge_color: Callout box and arrow color.
        font_size: Text font size in points.
    """

    text: str = "Annotation"
    x: float = 0.5
    y: float = 0.5
    xtext: float = 0.65
    ytext: float = 0.75
    arrow_style: str = "->"
    box_style: str = "round"
    face_color: str = "#ffffcc"
    edge_color: str = "#333333"
    font_size: float = 10.0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize this annotation, including base attributes."""
        data = super().to_dict()
        data.update(
            type="annotation",
            text=self.text,
            x=self.x,
            y=self.y,
            xtext=self.xtext,
            ytext=self.ytext,
            arrow_style=self.arrow_style,
            box_style=self.box_style,
            face_color=self.face_color,
            edge_color=self.edge_color,
            font_size=self.font_size,
        )
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnnotationModel":
        """Reconstruct an :class:`AnnotationModel` from serialized data."""
        obj = cls(
            text=data.get("text", "Annotation"),
            x=data.get("x", 0.5),
            y=data.get("y", 0.5),
            xtext=data.get("xtext", 0.65),
            ytext=data.get("ytext", 0.75),
            arrow_style=data.get("arrow_style", "->"),
            box_style=data.get("box_style", "round"),
            face_color=data.get("face_color", "#ffffcc"),
            edge_color=data.get("edge_color", "#333333"),
            font_size=data.get("font_size", 10.0),
        )
        obj.apply_base(data)
        return obj
