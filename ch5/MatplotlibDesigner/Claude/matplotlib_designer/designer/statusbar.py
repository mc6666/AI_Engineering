"""The application status bar: active tool, selection count, cursor position."""
from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QLabel, QStatusBar, QWidget


class DesignerStatusBar(QStatusBar):
    """Shows the active tool, current selection size, and undo/redo state."""

    def __init__(self, canvas, undo_manager, parent: Optional[QWidget] = None) -> None:
        """Wire the status bar up to the canvas and undo manager.

        Args:
            canvas: The :class:`~matplotlib_designer.designer.canvas.SceneCanvas`.
            undo_manager: Shared undo/redo stack.
            parent: Optional Qt parent widget.
        """
        super().__init__(parent)
        self._tool_label = QLabel("Tool: Selection")
        self._selection_label = QLabel("Selection: none")
        self._undo_label = QLabel("")
        self.addWidget(self._tool_label)
        self.addWidget(self._selection_label, 1)
        self.addPermanentWidget(self._undo_label)

        canvas.selection_changed.connect(self._on_selection_changed)
        undo_manager.changed.connect(lambda: self._on_undo_changed(undo_manager))
        self._on_undo_changed(undo_manager)

    def set_tool(self, name: str) -> None:
        """Update the displayed active tool name.

        Args:
            name: Human readable tool name, e.g. ``"Rectangle"``.
        """
        self._tool_label.setText(f"Tool: {name}")

    def _on_selection_changed(self, selection: list) -> None:
        if not selection:
            self._selection_label.setText("Selection: none")
        elif len(selection) == 1:
            self._selection_label.setText(f"Selection: {selection[0].name}")
        else:
            self._selection_label.setText(f"Selection: {len(selection)} objects")

    def _on_undo_changed(self, undo_manager) -> None:
        undo_text = f"Undo: {undo_manager.undo_label}" if undo_manager.can_undo else "Undo: —"
        redo_text = f"Redo: {undo_manager.redo_label}" if undo_manager.can_redo else "Redo: —"
        self._undo_label.setText(f"{undo_text}    {redo_text}")
