"""Dialog for laying out a grid of subplots (GridSpec-style)."""
from __future__ import annotations

from typing import Optional, Tuple

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QSpinBox, QWidget


class SubplotsDialog(QDialog):
    """Prompts for a rows x cols grid used to replace the figure's axes."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the dialog defaulting to a single 1x1 grid.

        Args:
            parent: Optional Qt parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle("Multiple Subplots")
        form = QFormLayout(self)

        self._rows = QSpinBox()
        self._rows.setRange(1, 10)
        self._rows.setValue(1)
        form.addRow("Rows", self._rows)

        self._cols = QSpinBox()
        self._cols.setRange(1, 10)
        self._cols.setValue(1)
        form.addRow("Columns", self._cols)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def values(self) -> Tuple[int, int]:
        """Return the chosen ``(rows, cols)``."""
        return (self._rows.value(), self._cols.value())
