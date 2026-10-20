"""Command that adds an axes to the figure."""
from __future__ import annotations

from typing import Callable

from ..models.figure_model import FigureModel
from ..models.axes_model import AxesModel
from .command import Command


class AddAxesCommand(Command):
    """Adds an :class:`AxesModel` to the figure's axes list."""

    def __init__(self, figure: FigureModel, axes: AxesModel, on_change: Callable[[], None]) -> None:
        """Initialize the command.

        Args:
            figure: The figure the axes will be added to.
            axes: The axes to add.
            on_change: Callback invoked after the scene changes.
        """
        self.label = "Add Axes"
        self._figure = figure
        self._axes = axes
        self._on_change = on_change

    def execute(self) -> None:
        """Append the axes to the figure."""
        self._figure.axes.append(self._axes)
        self._on_change()

    def undo(self) -> None:
        """Remove the axes from the figure."""
        if self._axes in self._figure.axes:
            self._figure.axes.remove(self._axes)
        self._on_change()
