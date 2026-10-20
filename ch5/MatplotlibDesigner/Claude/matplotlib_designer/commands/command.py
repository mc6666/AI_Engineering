"""The :class:`Command` interface underlying every undoable action."""
from __future__ import annotations

from abc import ABC, abstractmethod


class Command(ABC):
    """Interface every undoable action in the application must implement.

    Every user action that mutates the design document (adding an object,
    moving it, resizing it, changing a property, deleting it) is expressed
    as a :class:`Command` subclass and pushed onto the
    :class:`~matplotlib_designer.commands.undo.UndoManager` stack.

    Attributes:
        label: A short, human readable description shown in Edit menu
            entries such as "Undo Move Text".
    """

    label: str = "Action"

    @abstractmethod
    def execute(self) -> None:
        """Apply the action for the first time."""
        raise NotImplementedError

    @abstractmethod
    def undo(self) -> None:
        """Reverse the effect of :meth:`execute`."""
        raise NotImplementedError

    def redo(self) -> None:
        """Re-apply the action after it has been undone.

        The default implementation simply calls :meth:`execute` again,
        which is correct for any command whose ``execute`` is idempotent
        given the state ``undo`` restores. Override if that does not hold.
        """
        self.execute()
