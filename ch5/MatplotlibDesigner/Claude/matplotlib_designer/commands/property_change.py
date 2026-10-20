"""Generic single-attribute property change command used by the property panel."""
from __future__ import annotations

from typing import Any, Callable

from .command import Command


class PropertyChangeCommand(Command):
    """Sets a single attribute on a model object, with undo support.

    Backs almost every edit made through the property panel (font, color,
    line style, alignment, visibility, opacity, ...): the panel only needs
    to know the attribute name and the new value, this command handles
    capturing the old value and wiring it into the undo stack.
    """

    def __init__(self, obj: Any, attr: str, new_value: Any, on_change: Callable[[], None]) -> None:
        """Initialize the command.

        Args:
            obj: The model object whose attribute will change.
            attr: Name of the attribute to set (via ``setattr``/``getattr``).
            new_value: The value to assign.
            on_change: Callback invoked after the scene changes.
        """
        self.label = f"Change {attr.replace('_', ' ').title()}"
        self._obj = obj
        self._attr = attr
        self._old_value = getattr(obj, attr)
        self._new_value = new_value
        self._on_change = on_change

    def execute(self) -> None:
        """Apply the new attribute value."""
        setattr(self._obj, self._attr, self._new_value)
        self._on_change()

    def undo(self) -> None:
        """Restore the previous attribute value."""
        setattr(self._obj, self._attr, self._old_value)
        self._on_change()
