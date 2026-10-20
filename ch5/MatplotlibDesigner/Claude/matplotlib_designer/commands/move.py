"""Command that moves a scene object from one position to another."""
from __future__ import annotations

from typing import Any, Callable, Tuple

from .command import Command


class MoveObjectCommand(Command):
    """Restores or re-applies a position captured before/after a drag.

    Canvas dragging applies position changes live (for responsiveness) by
    calling ``apply_position`` directly on every mouse-move event. Once the
    gesture ends, a :class:`MoveObjectCommand` is pushed with
    :meth:`~matplotlib_designer.commands.undo.UndoManager.push_applied` so
    the already-applied change becomes a single undoable step.

    Position is deliberately generic (a tuple of floats) so the same
    command works for a :class:`~matplotlib_designer.models.text_model.TextModel`
    (``x, y``), a :class:`~matplotlib_designer.models.shape_model.ShapeModel`
    (``x, y``), an annotation's text box (``xtext, ytext``), or an axes'
    full ``(left, bottom, width, height)`` rectangle.
    """

    def __init__(
        self,
        name: str,
        apply_position: Callable[[Tuple[float, ...]], None],
        old_position: Tuple[float, ...],
        new_position: Tuple[float, ...],
        on_change: Callable[[], None],
    ) -> None:
        """Initialize the command.

        Args:
            name: Name of the object being moved, used to build the label.
            apply_position: Setter that applies a position tuple to the model.
            old_position: Position before the move.
            new_position: Position after the move.
            on_change: Callback invoked after the scene changes.
        """
        self.label = f"Move {name}"
        self._apply = apply_position
        self._old = old_position
        self._new = new_position
        self._on_change = on_change

    def execute(self) -> None:
        """Apply the new position."""
        self._apply(self._new)
        self._on_change()

    def undo(self) -> None:
        """Restore the old position."""
        self._apply(self._old)
        self._on_change()
