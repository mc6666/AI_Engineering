"""Dialog for exporting the current figure to any supported format."""
from __future__ import annotations

from typing import Optional, Tuple

from PySide6.QtWidgets import QFileDialog, QWidget

#: Maps the file dialog's filter string to an internal format key.
_FILTERS = [
    ("PNG Image (*.png)", "png"),
    ("PDF Document (*.pdf)", "pdf"),
    ("SVG Vector (*.svg)", "svg"),
    ("EPS Vector (*.eps)", "eps"),
    ("JPEG Image (*.jpg)", "jpg"),
    ("TIFF Image (*.tiff)", "tiff"),
    ("Python Script (*.py)", "py"),
    ("Project JSON (*.json)", "json"),
    ("Pickled Figure (*.pickle)", "pickle"),
]


class ExportDialog:
    """Namespace for the export file-picker (no state, just a static helper)."""

    @staticmethod
    def get_export_path(parent: Optional[QWidget] = None) -> Optional[Tuple[str, str]]:
        """Prompt the user for an export destination and format.

        Args:
            parent: Optional parent widget for the native dialog.

        Returns:
            A ``(file_path, format_key)`` tuple, or ``None`` if cancelled.
        """
        filter_string = ";;".join(f for f, _ in _FILTERS)
        path, chosen_filter = QFileDialog.getSaveFileName(parent, "Export Figure", "", filter_string)
        if not path:
            return None
        format_key = next((key for label, key in _FILTERS if label == chosen_filter), "png")
        return (path, format_key)
