"""Command that deletes a scene object from whichever list contains it."""
from __future__ import annotations

from typing import Any, Callable, List

from ..models.base_model import SceneObject
from .command import Command


class DeleteObjectCommand(Command):
    """Removes an object from its parent container, remembering its index.

    Works for any object living in a plain list: an axes in
    ``figure.axes``, or a plot/text/shape/annotation in the corresponding
    list on an :class:`~matplotlib_designer.models.axes_model.AxesModel`.
    """

    def __init__(self, container: List[Any], obj: SceneObject, on_change: Callable[[], None]) -> None:
        """Initialize the command.

        Args:
            container: The list the object currently lives in.
            obj: The object to delete.
            on_change: Callback invoked after the scene changes.
        """
        self.label = f"Delete {obj.name}"
        self._container = container
        self._obj = obj
        self._index = 0
        self._on_change = on_change

    def execute(self) -> None:
        """Remove the object, recording its position for undo."""
        self._index = self._container.index(self._obj)
        self._container.remove(self._obj)
        self._on_change()

    def undo(self) -> None:
        """Reinsert the object at its original position."""
        index = min(self._index, len(self._container))
        self._container.insert(index, self._obj)
        self._on_change()
