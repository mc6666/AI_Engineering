"""Command that adds a text object to an axes."""
from __future__ import annotations

from typing import Callable, List

from ..models.axes_model import AxesModel
from ..models.text_model import TextModel
from .command import Command


class AddTextCommand(Command):
    """Adds a free-floating :class:`TextModel` to an axes' text list."""

    def __init__(self, axes: AxesModel, text: TextModel, on_change: Callable[[], None]) -> None:
        """Initialize the command.

        Args:
            axes: The axes the text will be added to.
            text: The text object to add.
            on_change: Callback invoked after the scene changes, to trigger
                a canvas redraw and object tree refresh.
        """
        self.label = "Add Text"
        self._axes = axes
        self._text = text
        self._on_change = on_change

    def execute(self) -> None:
        """Append the text object to the axes."""
        self._axes.texts.append(self._text)
        self._on_change()

    def undo(self) -> None:
        """Remove the text object from the axes."""
        if self._text in self._axes.texts:
            self._axes.texts.remove(self._text)
        self._on_change()
