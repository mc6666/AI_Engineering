"""A small button that shows and edits a color via the native color dialog."""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QPushButton, QWidget


class ColorButton(QPushButton):
    """A flat-colored button; clicking it opens a color picker.

    Attributes:
        color_changed: Emitted with the new color as a ``"#rrggbb"`` string
            (or ``"none"`` if the user picks a fully transparent color).
    """

    color_changed = Signal(str)

    def __init__(self, color: str = "#000000", allow_none: bool = False, parent: Optional[QWidget] = None) -> None:
        """Initialize the button.

        Args:
            color: Initial color, as a hex string or ``"none"``.
            allow_none: Whether to offer a "No Color" option in the dialog.
            parent: Optional Qt parent widget.
        """
        super().__init__(parent)
        self._allow_none = allow_none
        self.setFixedWidth(48)
        self.set_color(color)
        self.clicked.connect(self._pick_color)

    def set_color(self, color: str) -> None:
        """Set the displayed color without emitting :attr:`color_changed`.

        Args:
            color: New color, as a hex string or ``"none"``.
        """
        self._color = color
        if color == "none":
            self.setText("None")
            self.setStyleSheet("")
        else:
            self.setText("")
            self.setStyleSheet(f"background-color: {color}; border: 1px solid #888;")

    @property
    def color(self) -> str:
        """The current color value."""
        return self._color

    def _pick_color(self) -> None:
        initial = QColor(self._color) if self._color != "none" else QColor("#ffffff")
        options = QColorDialog.ShowAlphaChannel
        picked = QColorDialog.getColor(initial, self, "Choose Color", options)
        if not picked.isValid():
            return
        new_color = picked.name()
        self.set_color(new_color)
        self.color_changed.emit(new_color)
