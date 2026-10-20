"""Dialog for creating a new figure document (File > New)."""
from __future__ import annotations

from typing import Optional, Tuple

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout, QSpinBox, QWidget

from ..widgets.color_button import ColorButton


class NewFigureDialog(QDialog):
    """Prompts for the size, resolution and background of a new figure."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the dialog with sensible Matplotlib defaults.

        Args:
            parent: Optional Qt parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle("New Figure")
        form = QFormLayout(self)

        self._width = QDoubleSpinBox()
        self._width.setRange(1, 100)
        self._width.setValue(8.0)
        form.addRow("Width (in)", self._width)

        self._height = QDoubleSpinBox()
        self._height.setRange(1, 100)
        self._height.setValue(6.0)
        form.addRow("Height (in)", self._height)

        self._dpi = QSpinBox()
        self._dpi.setRange(10, 1200)
        self._dpi.setValue(100)
        form.addRow("DPI", self._dpi)

        self._color = ColorButton("#ffffff")
        form.addRow("Background", self._color)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def values(self) -> Tuple[float, float, int, str]:
        """Return the chosen ``(width_in, height_in, dpi, facecolor)``."""
        return (self._width.value(), self._height.value(), self._dpi.value(), self._color.color)
