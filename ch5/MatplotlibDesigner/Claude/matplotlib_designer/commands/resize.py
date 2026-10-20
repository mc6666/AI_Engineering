"""Command that resizes a scene object from one size to another."""
from __future__ import annotations

from typing import Callable, Tuple

from .command import Command


class ResizeObjectCommand(Command):
    """Restores or re-applies a size/rect captured before/after a resize drag.

    Mirrors :class:`~matplotlib_designer.commands.move.MoveObjectCommand`
    but is kept as a distinct class so undo labels read "Resize X" rather
    than "Move X", and so future size-specific validation (minimum size,
    aspect-ratio lock) has a natural home.
    """

    def __init__(
        self,
        name: str,
        apply_size: Callable[[Tuple[float, ...]], None],
        old_size: Tuple[float, ...],
        new_size: Tuple[float, ...],
        on_change: Callable[[], None],
    ) -> None:
        """Initialize the command.

        Args:
            name: Name of the object being resized, used to build the label.
            apply_size: Setter that applies a size/rect tuple to the model.
            old_size: Size before the resize.
            new_size: Size after the resize.
            on_change: Callback invoked after the scene changes.
        """
        self.label = f"Resize {name}"
        self._apply = apply_size
        self._old = old_size
        self._new = new_size
        self._on_change = on_change

    def execute(self) -> None:
        """Apply the new size."""
        self._apply(self._new)
        self._on_change()

    def undo(self) -> None:
        """Restore the old size."""
        self._apply(self._old)
        self._on_change()
