"""Command that adds a vector shape to an axes."""
from __future__ import annotations

from typing import Callable

from ..models.axes_model import AxesModel
from ..models.shape_model import ShapeModel
from .command import Command


class AddShapeCommand(Command):
    """Adds a :class:`ShapeModel` (rectangle, ellipse, line, ...) to an axes."""

    def __init__(self, axes: AxesModel, shape: ShapeModel, on_change: Callable[[], None]) -> None:
        """Initialize the command.

        Args:
            axes: The axes the shape will be added to.
            shape: The shape object to add.
            on_change: Callback invoked after the scene changes.
        """
        self.label = f"Add {shape.kind.title()}"
        self._axes = axes
        self._shape = shape
        self._on_change = on_change

    def execute(self) -> None:
        """Append the shape to the axes."""
        self._axes.shapes.append(self._shape)
        self._on_change()

    def undo(self) -> None:
        """Remove the shape from the axes."""
        if self._shape in self._axes.shapes:
            self._axes.shapes.remove(self._shape)
        self._on_change()
