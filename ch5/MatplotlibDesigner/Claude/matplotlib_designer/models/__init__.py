"""Data models for Matplotlib Designer.

This package contains plain-dataclass models that represent the design-time
state of a figure (figure, axes, plots, text, shapes, annotations). Models
are pure data: they hold no references to Qt or Matplotlib objects, so they
can be freely serialized to JSON and rendered by
:mod:`matplotlib_designer.designer.canvas`.
"""

from .base_model import SceneObject, next_id
from .text_model import TextModel
from .shape_model import ShapeModel
from .annotation_model import AnnotationModel
from .plot_model import PlotModel
from .axes_model import AxesModel
from .figure_model import FigureModel

__all__ = [
    "SceneObject",
    "next_id",
    "TextModel",
    "ShapeModel",
    "AnnotationModel",
    "PlotModel",
    "AxesModel",
    "FigureModel",
]
