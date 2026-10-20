"""Tests for the command pattern: execute/undo/redo semantics."""
from __future__ import annotations

from matplotlib_designer.commands.add_text import AddTextCommand
from matplotlib_designer.commands.delete import DeleteObjectCommand
from matplotlib_designer.commands.property_change import PropertyChangeCommand
from matplotlib_designer.commands.redo import MacroCommand
from matplotlib_designer.commands.undo import UndoManager
from matplotlib_designer.models.axes_model import AxesModel
from matplotlib_designer.models.text_model import TextModel


def test_add_text_command_execute_and_undo():
    axes = AxesModel()
    text = TextModel(content="Hi")
    calls = []
    command = AddTextCommand(axes, text, lambda: calls.append(1))
    command.execute()
    assert text in axes.texts
    command.undo()
    assert text not in axes.texts
    assert calls == [1, 1]


def test_undo_manager_push_and_undo_redo():
    axes = AxesModel()
    text = TextModel(content="Hi")
    manager = UndoManager()
    manager.push(AddTextCommand(axes, text, lambda: None))
    assert text in axes.texts
    assert manager.can_undo
    manager.undo()
    assert text not in axes.texts
    assert manager.can_redo
    manager.redo()
    assert text in axes.texts


def test_property_change_command_round_trip():
    text = TextModel(content="Old")
    manager = UndoManager()
    manager.push(PropertyChangeCommand(text, "content", "New", lambda: None))
    assert text.content == "New"
    manager.undo()
    assert text.content == "Old"


def test_delete_object_command_restores_index():
    axes = AxesModel()
    t1, t2, t3 = TextModel(name="a"), TextModel(name="b"), TextModel(name="c")
    axes.texts.extend([t1, t2, t3])
    command = DeleteObjectCommand(axes.texts, t2, lambda: None)
    command.execute()
    assert axes.texts == [t1, t3]
    command.undo()
    assert axes.texts == [t1, t2, t3]


def test_macro_command_groups_undo():
    axes = AxesModel()
    t1, t2 = TextModel(name="a"), TextModel(name="b")
    macro = MacroCommand([
        AddTextCommand(axes, t1, lambda: None),
        AddTextCommand(axes, t2, lambda: None),
    ])
    macro.execute()
    assert axes.texts == [t1, t2]
    macro.undo()
    assert axes.texts == []


def test_unlimited_undo_stack_depth():
    axes = AxesModel()
    manager = UndoManager()
    texts = [TextModel(name=str(i)) for i in range(100)]
    for text in texts:
        manager.push(AddTextCommand(axes, text, lambda: None))
    for _ in range(100):
        manager.undo()
    assert axes.texts == []
    for _ in range(100):
        manager.redo()
    assert len(axes.texts) == 100
