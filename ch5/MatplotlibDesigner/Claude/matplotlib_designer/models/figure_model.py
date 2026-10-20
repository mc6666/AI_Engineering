"""Model for the top-level Figure: the root of the whole design document."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .base_model import SceneObject
from .axes_model import AxesModel


@dataclass
class FigureModel(SceneObject):
    """The root document model: a Matplotlib figure and its axes.

    Attributes:
        width_in: Figure width in inches.
        height_in: Figure height in inches.
        dpi: Dots-per-inch resolution used for rendering and raster export.
        facecolor: Figure background color.
        layout: Layout engine: ``"none"``, ``"tight"`` or ``"constrained"``.
        axes: All axes contained in the figure.
        suptitle: Optional figure-level super-title text, or ``""``.
    """

    width_in: float = 8.0
    height_in: float = 6.0
    dpi: int = 100
    facecolor: str = "#ffffff"
    layout: str = "none"
    axes: List[AxesModel] = field(default_factory=list)
    suptitle: str = ""

    def find(self, object_id: str) -> Optional[SceneObject]:
        """Find any scene object anywhere in the model tree by id.

        Args:
            object_id: The id to search for.

        Returns:
            The matching :class:`~matplotlib_designer.models.base_model.SceneObject`,
            or ``None`` if not found.
        """
        for axes in self.axes:
            if axes.id == object_id:
                return axes
            for child in (axes.title, axes.xlabel, axes.ylabel, *axes.all_children()):
                if child.id == object_id:
                    return child
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the whole figure document to a plain ``dict``."""
        data = super().to_dict()
        data.update(
            type="figure",
            width_in=self.width_in,
            height_in=self.height_in,
            dpi=self.dpi,
            facecolor=self.facecolor,
            layout=self.layout,
            axes=[a.to_dict() for a in self.axes],
            suptitle=self.suptitle,
        )
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FigureModel":
        """Reconstruct a :class:`FigureModel` document from serialized data."""
        obj = cls(
            width_in=data.get("width_in", 8.0),
            height_in=data.get("height_in", 6.0),
            dpi=data.get("dpi", 100),
            facecolor=data.get("facecolor", "#ffffff"),
            layout=data.get("layout", "none"),
            axes=[AxesModel.from_dict(a) for a in data.get("axes", [])],
            suptitle=data.get("suptitle", ""),
        )
        obj.apply_base(data)
        return obj

    @classmethod
    def new_default(cls) -> "FigureModel":
        """Create a fresh document with a single default axes.

        Returns:
            A new :class:`FigureModel` with one rectilinear axes filling
            the standard Matplotlib default position.
        """
        fig = cls(name="Figure")
        fig.axes.append(AxesModel(name="Axes 1"))
        return fig
