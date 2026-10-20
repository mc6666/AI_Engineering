"""Command that adds a data series (plot) to an axes."""
from __future__ import annotations

from typing import Callable

from ..models.axes_model import AxesModel
from ..models.plot_model import PlotModel
from .command import Command


class AddPlotCommand(Command):
    """Adds a :class:`PlotModel` data series to an axes."""

    def __init__(self, axes: AxesModel, plot: PlotModel, on_change: Callable[[], None]) -> None:
        """Initialize the command.

        Args:
            axes: The axes the plot series will be added to.
            plot: The plot series to add.
            on_change: Callback invoked after the scene changes.
        """
        self.label = f"Add {plot.kind.title()} Plot"
        self._axes = axes
        self._plot = plot
        self._on_change = on_change

    def execute(self) -> None:
        """Append the plot series to the axes."""
        self._axes.plots.append(self._plot)
        self._on_change()

    def undo(self) -> None:
        """Remove the plot series from the axes."""
        if self._plot in self._axes.plots:
            self._axes.plots.remove(self._plot)
        self._on_change()
