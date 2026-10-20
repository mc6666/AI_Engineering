"""Composite command support, used to make multi-step gestures one undo step."""
from __future__ import annotations

from typing import List

from .command import Command


class MacroCommand(Command):
    """Groups several commands so they undo/redo together as a single step.

    Used, for example, when deleting a multi-selection: each deleted object
    is its own :class:`~matplotlib_designer.commands.delete.DeleteObjectCommand`,
    but the user should only need one Ctrl+Z to bring all of them back.
    """

    def __init__(self, commands: List[Command], label: str = "Multiple Changes") -> None:
        """Initialize the macro.

        Args:
            commands: The sub-commands, in the order they should execute.
                They are undone in reverse order.
            label: Human readable label shown in the Edit menu.
        """
        self._commands = commands
        self.label = label

    def execute(self) -> None:
        """Execute every sub-command in order."""
        for command in self._commands:
            command.execute()

    def undo(self) -> None:
        """Undo every sub-command in reverse order."""
        for command in reversed(self._commands):
            command.undo()

    def redo(self) -> None:
        """Redo every sub-command in order."""
        for command in self._commands:
            command.redo()
