"""Tests for JSON project save/load round trips."""
from __future__ import annotations

from matplotlib_designer.models.figure_model import FigureModel
from matplotlib_designer.models.plot_model import PlotModel
from matplotlib_designer.models.shape_model import ShapeModel
from matplotlib_designer.serialization.project_serializer import load_project, save_project


def test_save_and_load_round_trip(tmp_path):
    figure = FigureModel.new_default()
    figure.axes[0].plots.append(PlotModel(kind="line", x=[1, 2, 3], y=[4, 5, 6], label="demo"))
    figure.axes[0].shapes.append(ShapeModel(kind="rectangle", x=0.2, y=0.2, width=0.3, height=0.1))
    figure.width_in = 10.0

    path = tmp_path / "project.json"
    save_project(figure, path)
    assert path.exists()

    loaded = load_project(path)
    assert loaded.width_in == 10.0
    assert len(loaded.axes) == 1
    assert loaded.axes[0].plots[0].label == "demo"
    assert loaded.axes[0].shapes[0].kind == "rectangle"


def test_load_project_rejects_foreign_json(tmp_path):
    path = tmp_path / "not_a_project.json"
    path.write_text('{"hello": "world"}', encoding="utf-8")
    try:
        load_project(path)
        assert False, "expected ValueError"
    except ValueError:
        pass
