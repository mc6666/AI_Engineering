"""Tests for the export backends: images, Python script generation, pickle."""
from __future__ import annotations

import pickle

from matplotlib_designer.commands.undo import UndoManager
from matplotlib_designer.designer.canvas import SceneCanvas
from matplotlib_designer.export.image_export import export_image
from matplotlib_designer.export.pickle_export import export_pickle
from matplotlib_designer.export.script_export import generate_script
from matplotlib_designer.models.figure_model import FigureModel
from matplotlib_designer.models.plot_model import PlotModel


def _demo_model() -> FigureModel:
    model = FigureModel.new_default()
    model.axes[0].plots.append(PlotModel(kind="line", x=[1, 2, 3], y=[3, 1, 2], label="demo"))
    model.axes[0].title.content = "Demo Title"
    return model


def test_export_image_png(qapp, tmp_path):
    model = _demo_model()
    canvas = SceneCanvas(model, UndoManager())
    path = tmp_path / "out.png"
    export_image(canvas, path, "png")
    assert path.exists()
    assert path.stat().st_size > 0


def test_export_image_rejects_unknown_format(qapp, tmp_path):
    model = _demo_model()
    canvas = SceneCanvas(model, UndoManager())
    try:
        export_image(canvas, tmp_path / "out.xyz", "xyz")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_export_pickle_round_trip(qapp, tmp_path):
    model = _demo_model()
    canvas = SceneCanvas(model, UndoManager())
    path = tmp_path / "out.pickle"
    export_pickle(canvas, path)
    with open(path, "rb") as handle:
        restored_figure = pickle.load(handle)
    assert restored_figure.get_axes()


def test_generate_script_contains_plot_and_title():
    model = _demo_model()
    script = generate_script(model)
    assert "ax1.plot(" in script
    assert "Demo Title" in script
    assert "import matplotlib.pyplot as plt" in script
