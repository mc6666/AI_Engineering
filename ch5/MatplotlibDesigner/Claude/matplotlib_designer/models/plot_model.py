"""Model for data-driven plot series (line, scatter, bar, heatmap, ...)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .base_model import SceneObject

#: Supported plot kinds. Kept as a plain tuple (not an Enum) so new plugin
#: plot types can extend it at runtime without modifying this module.
PLOT_KINDS = (
    "line",
    "scatter",
    "bar",
    "barh",
    "hist",
    "pie",
    "box",
    "violin",
    "stem",
    "step",
    "heatmap",
    "contour",
    "image",
    "errorbar",
    "stack",
    "area",
)


@dataclass
class PlotModel(SceneObject):
    """A single data series drawn inside an :class:`AxesModel`.

    Attributes:
        kind: One of :data:`PLOT_KINDS`.
        x: X data (or bin edges for 1-D kinds).
        y: Y data.
        yerr: Optional symmetric y error values, used by ``"errorbar"``.
        z: 2-D grid data for ``"heatmap"``/``"contour"``/``"image"``.
        label: Legend label.
        color: Primary color (line/marker/face color depending on kind).
        line_style: Matplotlib line style code.
        line_width: Line width in points.
        marker: Matplotlib marker code, empty for none.
        marker_size: Marker size in points.
        colormap: Colormap name used by ``"heatmap"``/``"contour"``/``"image"``.
    """

    kind: str = "line"
    x: List[float] = field(default_factory=list)
    y: List[float] = field(default_factory=list)
    yerr: Optional[List[float]] = None
    z: Optional[List[List[float]]] = None
    label: str = ""
    color: str = "#1f77b4"
    line_style: str = "-"
    line_width: float = 1.5
    marker: str = ""
    marker_size: float = 6.0
    colormap: str = "viridis"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize this plot series, including base attributes."""
        data = super().to_dict()
        data.update(
            type="plot",
            kind=self.kind,
            x=list(self.x),
            y=list(self.y),
            yerr=list(self.yerr) if self.yerr is not None else None,
            z=[list(row) for row in self.z] if self.z is not None else None,
            label=self.label,
            color=self.color,
            line_style=self.line_style,
            line_width=self.line_width,
            marker=self.marker,
            marker_size=self.marker_size,
            colormap=self.colormap,
        )
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlotModel":
        """Reconstruct a :class:`PlotModel` from serialized data."""
        obj = cls(
            kind=data.get("kind", "line"),
            x=list(data.get("x", [])),
            y=list(data.get("y", [])),
            yerr=list(data["yerr"]) if data.get("yerr") is not None else None,
            z=[list(row) for row in data["z"]] if data.get("z") is not None else None,
            label=data.get("label", ""),
            color=data.get("color", "#1f77b4"),
            line_style=data.get("line_style", "-"),
            line_width=data.get("line_width", 1.5),
            marker=data.get("marker", ""),
            marker_size=data.get("marker_size", 6.0),
            colormap=data.get("colormap", "viridis"),
        )
        obj.apply_base(data)
        return obj
