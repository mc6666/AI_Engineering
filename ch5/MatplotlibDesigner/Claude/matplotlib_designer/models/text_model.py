"""Model for text-like objects: titles, labels, tick labels and free text."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .base_model import SceneObject


@dataclass
class TextModel(SceneObject):
    """A single piece of text placed in figure- or axes-fraction coordinates.

    Attributes:
        kind: One of ``"text"``, ``"title"``, ``"subtitle"``, ``"xlabel"``,
            ``"ylabel"``.
        content: The text to display. May contain MathText (``$...$``).
        x: Horizontal anchor position (axes-fraction coordinates, 0-1).
        y: Vertical anchor position (axes-fraction coordinates, 0-1).
        font_family: Matplotlib font family name.
        font_size: Font size in points.
        bold: Whether the text is rendered bold.
        italic: Whether the text is rendered italic.
        underline: Whether the text is rendered underlined.
        color: Text color as a hex string or named color.
        background: Background (bbox) face color, or ``"none"``.
        ha: Horizontal alignment: ``"left"``, ``"center"``, ``"right"``.
        va: Vertical alignment: ``"top"``, ``"center"``, ``"bottom"``.
        rotation: Rotation angle in degrees.
        use_tex: Whether to render using the external LaTeX engine.
        wrap: Whether to auto-wrap long lines.
    """

    kind: str = "text"
    content: str = "Text"
    x: float = 0.5
    y: float = 0.5
    font_family: str = "DejaVu Sans"
    font_size: float = 12.0
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color: str = "#000000"
    background: str = "none"
    ha: str = "center"
    va: str = "center"
    rotation: float = 0.0
    use_tex: bool = False
    wrap: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize this text object, including base attributes."""
        data = super().to_dict()
        data.update(
            type="text",
            kind=self.kind,
            content=self.content,
            x=self.x,
            y=self.y,
            font_family=self.font_family,
            font_size=self.font_size,
            bold=self.bold,
            italic=self.italic,
            underline=self.underline,
            color=self.color,
            background=self.background,
            ha=self.ha,
            va=self.va,
            rotation=self.rotation,
            use_tex=self.use_tex,
            wrap=self.wrap,
        )
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TextModel":
        """Reconstruct a :class:`TextModel` from serialized data.

        Args:
            data: A dictionary previously produced by :meth:`to_dict`.

        Returns:
            The reconstructed model instance.
        """
        obj = cls(
            kind=data.get("kind", "text"),
            content=data.get("content", "Text"),
            x=data.get("x", 0.5),
            y=data.get("y", 0.5),
            font_family=data.get("font_family", "DejaVu Sans"),
            font_size=data.get("font_size", 12.0),
            bold=data.get("bold", False),
            italic=data.get("italic", False),
            underline=data.get("underline", False),
            color=data.get("color", "#000000"),
            background=data.get("background", "none"),
            ha=data.get("ha", "center"),
            va=data.get("va", "center"),
            rotation=data.get("rotation", 0.0),
            use_tex=data.get("use_tex", False),
            wrap=data.get("wrap", False),
        )
        obj.apply_base(data)
        return obj

    @property
    def font_style(self) -> str:
        """Return the Matplotlib ``fontstyle`` value (``"italic"``/``"normal"``)."""
        return "italic" if self.italic else "normal"

    @property
    def font_weight(self) -> str:
        """Return the Matplotlib ``fontweight`` value (``"bold"``/``"normal"``)."""
        return "bold" if self.bold else "normal"
