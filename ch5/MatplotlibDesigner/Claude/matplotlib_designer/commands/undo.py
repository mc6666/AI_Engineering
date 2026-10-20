"""Undo/redo stack manager shared by the whole application."""
from __future__ import annotations

from typing import Callable, List, Optional

from PySide6.QtCore import QObject, Signal

from .command import Command


class UndoManager(QObject):
    """Maintains the undo and redo stacks and drives their execution.

    The stack size is unbounded, satisfying the "unlimited undo/redo"
    acceptance criterion. Emits :attr:`changed` after every mutation so
    the UI (menu enabled state, status bar) can stay in sync.

    Attributes:
        changed: Signal emitted whenever the undo or redo stack changes.
    """

    changed = Signal()

    def __init__(self, on_change: Optional[Callable[[], None]] = None) -> None:
        """Initialize an empty undo manager.

        Args:
            on_change: Optional extra callback invoked after every mutation,
                in addition to the :attr:`changed` Qt signal.
        """
        super().__init__()
        self._undo_stack: List[Command] = []
        self._redo_stack: List[Command] = []
        self._on_change = on_change

    def push(self, command: Command) -> None:
        """Execute ``command`` and push it onto the undo stack.

        Args:
            command: The command to execute and record.
        """
        command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()
        self._notify()

    def push_applied(self, command: Command) -> None:
        """Record an already-applied command without re-executing it.

        Useful for interactive operations (dragging) where the model was
        already updated live during mouse movement; only the undo record
        needs to be created at the end of the gesture.

        Args:
            command: The command whose effect has already been applied.
        """
        self._undo_stack.append(command)
        self._redo_stack.clear()
        self._notify()

    def undo(self) -> None:
        """Undo the most recent command, if any."""
        if not self._undo_stack:
            return
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)
        self._notify()

    def redo(self) -> None:
        """Redo the most recently undone command, if any."""
        if not self._redo_stack:
            return
        command = self._redo_stack.pop()
        command.redo()
        self._undo_stack.append(command)
        self._notify()

    def clear(self) -> None:
        """Clear both stacks, e.g. when a new project is loaded."""
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._notify()

    @property
    def can_undo(self) -> bool:
        """Whether :meth:`undo` would have an effect."""
        return bool(self._undo_stack)

    @property
    def can_redo(self) -> bool:
        """Whether :meth:`redo` would have an effect."""
        return bool(self._redo_stack)

    @property
    def undo_label(self) -> str:
        """Label of the command that would be undone next, or ``""``."""
        return self._undo_stack[-1].label if self._undo_stack else ""

    @property
    def redo_label(self) -> str:
        """Label of the command that would be redone next, or ``""``."""
        return self._redo_stack[-1].label if self._redo_stack else ""

    def _notify(self) -> None:
        self.changed.emit()
        if self._on_change is not None:
            self._on_change()
