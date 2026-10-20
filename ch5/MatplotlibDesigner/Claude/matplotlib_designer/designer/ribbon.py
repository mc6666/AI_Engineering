"""A PowerPoint-style tabbed ribbon, grouping the same actions as the toolbar."""
from __future__ import annotations

from typing import Dict, List, Tuple

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QTabWidget, QToolBar, QWidget

#: Ribbon tabs: (tab title, [action keys in that group]).
RIBBON_GROUPS: List[Tuple[str, List[str]]] = [
    ("Home", ["select", "move", "zoom", "pan", "text", "annotation"]),
    ("Insert", ["rectangle", "ellipse", "line", "arrow", "image", "legend", "grid"]),
    ("Plot", ["line_plot", "scatter_plot", "bar_plot", "histogram", "heatmap", "subplots"]),
    ("Layout", ["title", "subtitle", "xlabel", "ylabel", "tick_editor", "export"]),
]


def build_ribbon(window, actions: Dict[str, QAction]) -> QTabWidget:
    """Build a tabbed ribbon widget reusing the shared action set.

    Args:
        window: The owning main window (used as the widget parent).
        actions: The action map returned by
            :func:`matplotlib_designer.designer.toolbar.create_actions`.

    Returns:
        A :class:`QTabWidget` with one tab per :data:`RIBBON_GROUPS` entry,
        each hosting a small toolbar of the group's actions.
    """
    ribbon = QTabWidget(window)
    ribbon.setObjectName("Ribbon")
    ribbon.setMaximumHeight(72)
    for title, keys in RIBBON_GROUPS:
        tab = QWidget()
        bar = QToolBar(tab)
        bar.setIconSize(bar.iconSize())
        for key in keys:
            bar.addAction(actions[key])
        from PySide6.QtWidgets import QHBoxLayout

        layout = QHBoxLayout(tab)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(bar)
        layout.addStretch(1)
        ribbon.addTab(tab, title)
    return ribbon
