"""Tests for the dataclass models: construction and to_dict/from_dict round trips."""
from __future__ import annotations

from matplotlib_designer.models.annotation_model import AnnotationModel
from matplotlib_designer.models.axes_model import AxesModel
from matplotlib_designer.models.figure_model import FigureModel
from matplotlib_designer.models.plot_model import PlotModel
from matplotlib_designer.models.shape_model import ShapeModel
from matplotlib_designer.models.text_model import TextModel


def test_text_model_round_trip():
    text = TextModel(content="Hello", x=0.2, y=0.3, bold=True, color="#ff0000")
    restored = TextModel.from_dict(text.to_dict())
    assert restored.content == "Hello"
    assert restored.x == 0.2
    assert restored.bold is True
    assert restored.id == text.id


def test_shape_model_round_trip():
    shape = ShapeModel(kind="rectangle", x=0.1, y=0.1, width=0.4, height=0.2, points=[(0.0, 0.0), (1.0, 1.0)])
    restored = ShapeModel.from_dict(shape.to_dict())
    assert restored.kind == "rectangle"
    assert restored.points == [(0.0, 0.0), (1.0, 1.0)]


def test_annotation_model_round_trip():
    annotation = AnnotationModel(text="Peak", x=0.5, y=0.5, xtext=0.7, ytext=0.8)
    restored = AnnotationModel.from_dict(annotation.to_dict())
    assert restored.text == "Peak"
    assert restored.xtext == 0.7


def test_plot_model_round_trip_with_grid_data():
    plot = PlotModel(kind="heatmap", z=[[1, 2], [3, 4]])
    restored = PlotModel.from_dict(plot.to_dict())
    assert restored.z == [[1, 2], [3, 4]]


def test_figure_model_new_default_has_one_axes():
    figure = FigureModel.new_default()
    assert len(figure.axes) == 1
    assert isinstance(figure.axes[0], AxesModel)


def test_figure_model_find_locates_nested_object():
    figure = FigureModel.new_default()
    text = TextModel(content="Note")
    figure.axes[0].texts.append(text)
    found = figure.find(text.id)
    assert found is text


def test_figure_model_round_trip_preserves_hierarchy():
    figure = FigureModel.new_default()
    figure.axes[0].plots.append(PlotModel(kind="line", x=[1, 2], y=[3, 4], label="series"))
    figure.axes[0].shapes.append(ShapeModel(kind="ellipse"))
    restored = FigureModel.from_dict(figure.to_dict())
    assert len(restored.axes) == 1
    assert restored.axes[0].plots[0].label == "series"
    assert restored.axes[0].shapes[0].kind == "ellipse"
