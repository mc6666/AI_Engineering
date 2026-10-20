"""A combo box for picking a Matplotlib-usable font family."""
from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QComboBox, QWidget

#: A conservative set of font families available in every Matplotlib install
#: (bundled DejaVu/STIX fonts) plus common system fonts.
FONT_FAMILIES = [
    "DejaVu Sans", "DejaVu Serif", "DejaVu Sans Mono",
    "STIXGeneral", "Arial", "Helvetica", "Times New Roman", "Courier New",
]


class FontSelector(QComboBox):
    """Editable combo box listing common font families."""

    def __init__(self, current: str = "DejaVu Sans", parent: Optional[QWidget] = None) -> None:
        """Initialize the selector.

        Args:
            current: The initially selected font family.
            parent: Optional Qt parent widget.
        """
        super().__init__(parent)
        self.setEditable(True)
        self.addItems(FONT_FAMILIES)
        self.setCurrentText(current)
