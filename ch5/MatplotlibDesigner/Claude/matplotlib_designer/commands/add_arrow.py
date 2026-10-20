"""Command that adds an arrow/callout annotation to an axes."""
from __future__ import annotations

from typing import Callable

from ..models.axes_model import AxesModel
from ..models.annotation_model import AnnotationModel
from .command import Command


class AddAnnotationCommand(Command):
    """Adds an :class:`AnnotationModel` (arrow + text callout) to an axes."""

    def __init__(self, axes: AxesModel, annotation: AnnotationModel, on_change: Callable[[], None]) -> None:
        """Initialize the command.

        Args:
            axes: The axes the annotation will be added to.
            annotation: The annotation object to add.
            on_change: Callback invoked after the scene changes.
        """
        self.label = "Add Annotation"
        self._axes = axes
        self._annotation = annotation
        self._on_change = on_change

    def execute(self) -> None:
        """Append the annotation to the axes."""
        self._axes.annotations.append(self._annotation)
        self._on_change()

    def undo(self) -> None:
        """Remove the annotation from the axes."""
        if self._annotation in self._axes.annotations:
            self._axes.annotations.remove(self._annotation)
        self._on_change()
