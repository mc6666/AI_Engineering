"""Tests for the interactive canvas: rendering, selection and hit-testing."""
from __future__ import annotations

from matplotlib_designer.commands.undo import UndoManager
from matplotlib_designer.designer.canvas import SceneCanvas, axes_to_fig_point
from matplotlib_designer.models.figure_model import FigureModel
from matplotlib_designer.models.shape_model import ShapeModel
from matplotlib_designer.models.text_model import TextModel


def test_canvas_builds_figure_from_model(qapp):
    model = FigureModel.new_default()
    canvas = SceneCanvas(model, UndoManager())
    assert canvas.figure is not None
    # One real axes plus the selection overlay axes.
    assert len(canvas.figure.axes) == 2


def test_hit_test_finds_shape(qapp):
    model = FigureModel.new_default()
    axes = model.axes[0]
    shape = ShapeModel(kind="rectangle", x=0.3, y=0.3, width=0.2, height=0.2)
    axes.shapes.append(shape)
    canvas = SceneCanvas(model, UndoManager())
    canvas.rebuild()

    center = axes_to_fig_point(axes.position, (0.4, 0.4))
    hit = canvas.hit_test(*center)
    assert hit is not None
    assert hit[1] is shape


def test_hit_test_empty_area_returns_none(qapp):
    model = FigureModel.new_default()
    canvas = SceneCanvas(model, UndoManager())
    hit = canvas.hit_test(0.0, 0.0)
    assert hit is None


def test_selection_move_updates_model(qapp):
    model = FigureModel.new_default()
    axes = model.axes[0]
    text = TextModel(content="Hi", x=0.5, y=0.5)
    axes.texts.append(text)
    canvas = SceneCanvas(model, UndoManager())
    canvas.rebuild()

    old_pos = canvas.get_object_position(text)
    new_fig_pos = (old_pos[0] + 0.05, old_pos[1] + 0.05)
    canvas.set_object_position(text, new_fig_pos)
    assert text.x != 0.5

    canvas.commit_move(text, old_pos, new_fig_pos)
    assert canvas.undo_manager.can_undo
    canvas.undo_manager.undo()
    assert round(text.x, 6) == 0.5


def test_delete_selection_removes_object(qapp):
    model = FigureModel.new_default()
    axes = model.axes[0]
    text = TextModel(content="Hi")
    axes.texts.append(text)
    canvas = SceneCanvas(model, UndoManager())
    canvas.set_selection([text])
    canvas.delete_selection()
    assert text not in axes.texts
    canvas.undo_manager.undo()
    assert text in axes.texts
