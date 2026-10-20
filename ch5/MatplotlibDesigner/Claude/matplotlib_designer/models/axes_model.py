"""Model for a single Matplotlib Axes and everything drawn inside it."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .base_model import SceneObject
from .text_model import TextModel
from .plot_model import PlotModel
from .shape_model import ShapeModel
from .annotation_model import AnnotationModel


def _default_title() -> TextModel:
    return TextModel(name="Title", kind="title", content="", x=0.5, y=1.0, va="bottom", font_size=13.0)


def _default_xlabel() -> TextModel:
    return TextModel(name="X Label", kind="xlabel", content="", x=0.5, y=-0.08, va="top", font_size=11.0)


def _default_ylabel() -> TextModel:
    return TextModel(name="Y Label", kind="ylabel", content="", x=-0.08, y=0.5, ha="right", rotation=90, font_size=11.0)


@dataclass
class AxesModel(SceneObject):
    """A rectangular (or polar/3D) plotting region within the figure.

    Attributes:
        position: ``(left, bottom, width, height)`` in figure-fraction
            coordinates, matching :meth:`matplotlib.figure.Figure.add_axes`.
        projection: ``"rectilinear"``, ``"polar"`` or ``"3d"``.
        title: Title text object.
        xlabel: X axis label text object.
        ylabel: Y axis label text object.
        show_grid: Whether the axes grid is drawn.
        show_legend: Whether a legend is drawn for the plots in this axes.
        legend_loc: Matplotlib legend location string.
        facecolor: Axes background color.
        plots: Data series drawn in this axes.
        texts: Free-floating text objects anchored to this axes.
        shapes: Vector shapes anchored to this axes.
        annotations: Callout annotations anchored to this axes.
        twin_of: Id of another :class:`AxesModel` this axes shares an axis
            with (twinx/twiny), or ``None``.
        twin_axis: ``"x"`` or ``"y"`` indicating which axis is shared when
            ``twin_of`` is set.
        inset_of: Id of the parent axes if this is an inset axes.
    """

    position: Tuple[float, float, float, float] = (0.125, 0.11, 0.775, 0.77)
    projection: str = "rectilinear"
    title: TextModel = field(default_factory=_default_title)
    xlabel: TextModel = field(default_factory=_default_xlabel)
    ylabel: TextModel = field(default_factory=_default_ylabel)
    show_grid: bool = False
    show_legend: bool = False
    legend_loc: str = "best"
    facecolor: str = "#ffffff"
    plots: List[PlotModel] = field(default_factory=list)
    texts: List[TextModel] = field(default_factory=list)
    shapes: List[ShapeModel] = field(default_factory=list)
    annotations: List[AnnotationModel] = field(default_factory=list)
    twin_of: Optional[str] = None
    twin_axis: Optional[str] = None
    inset_of: Optional[str] = None

    def all_children(self) -> List[SceneObject]:
        """Return every child scene object (plots, texts, shapes, annotations).

        Returns:
            A flat list combining all child collections, useful for the
            object tree and for hit-testing during selection.
        """
        return [*self.plots, *self.texts, *self.shapes, *self.annotations]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize this axes and all of its children, including base attributes."""
        data = super().to_dict()
        data.update(
            type="axes",
            position=list(self.position),
            projection=self.projection,
            title=self.title.to_dict(),
            xlabel=self.xlabel.to_dict(),
            ylabel=self.ylabel.to_dict(),
            show_grid=self.show_grid,
            show_legend=self.show_legend,
            legend_loc=self.legend_loc,
            facecolor=self.facecolor,
            plots=[p.to_dict() for p in self.plots],
            texts=[t.to_dict() for t in self.texts],
            shapes=[s.to_dict() for s in self.shapes],
            annotations=[a.to_dict() for a in self.annotations],
            twin_of=self.twin_of,
            twin_axis=self.twin_axis,
            inset_of=self.inset_of,
        )
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AxesModel":
        """Reconstruct an :class:`AxesModel` (and its children) from serialized data."""
        obj = cls(
            position=tuple(data.get("position", (0.125, 0.11, 0.775, 0.77))),
            projection=data.get("projection", "rectilinear"),
            title=TextModel.from_dict(data["title"]) if data.get("title") else _default_title(),
            xlabel=TextModel.from_dict(data["xlabel"]) if data.get("xlabel") else _default_xlabel(),
            ylabel=TextModel.from_dict(data["ylabel"]) if data.get("ylabel") else _default_ylabel(),
            show_grid=data.get("show_grid", False),
            show_legend=data.get("show_legend", False),
            legend_loc=data.get("legend_loc", "best"),
            facecolor=data.get("facecolor", "#ffffff"),
            plots=[PlotModel.from_dict(p) for p in data.get("plots", [])],
            texts=[TextModel.from_dict(t) for t in data.get("texts", [])],
            shapes=[ShapeModel.from_dict(s) for s in data.get("shapes", [])],
            annotations=[AnnotationModel.from_dict(a) for a in data.get("annotations", [])],
            twin_of=data.get("twin_of"),
            twin_axis=data.get("twin_axis"),
            inset_of=data.get("inset_of"),
        )
        obj.apply_base(data)
        return obj
