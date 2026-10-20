"""Toolbar actions shared by the classic toolbar and the tabbed ribbon.

:func:`create_actions` builds every :class:`QAction` exactly once; both
:func:`build_toolbar` (a flat classic toolbar) and
:mod:`matplotlib_designer.designer.ribbon` (a grouped, tabbed layout) reuse
the same action objects, since a Qt ``QAction`` can be shared by multiple
toolbars/menus.
"""
from __future__ import annotations

from typing import Dict

from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QToolBar

#: Ordered list of ``(key, label, checkable)`` for every tool/insert action.
TOOL_ACTIONS = [
    ("select", "Selection", True),
    ("move", "Move", True),
    ("zoom", "Zoom", True),
    ("pan", "Pan", True),
    ("text", "Text", True),
    ("annotation", "Annotation", True),
    ("arrow", "Arrow", True),
    ("rectangle", "Rectangle", True),
    ("ellipse", "Ellipse", True),
    ("line", "Line", True),
]


def create_actions(window) -> Dict[str, QAction]:
    """Create every toolbar/ribbon action, bound to ``window`` callbacks.

    Args:
        window: The :class:`~matplotlib_designer.designer.main_window.MainWindow`
            instance; used both as the parent for the actions and as the
            source of the callback methods they trigger.

    Returns:
        A mapping from action key (e.g. ``"select"``, ``"line_plot"``) to
        the created :class:`QAction`.
    """
    actions: Dict[str, QAction] = {}
    tool_group = QActionGroup(window)
    tool_group.setExclusive(True)
    for key, label, checkable in TOOL_ACTIONS:
        action = QAction(label, window)
        action.setCheckable(checkable)
        tool_key = "select" if key == "move" else key
        action.triggered.connect(lambda _checked=False, k=tool_key: window.set_active_tool(k))
        tool_group.addAction(action)
        actions[key] = action
    actions["select"].setChecked(True)

    for key, label in [("title", "Title"), ("subtitle", "Subtitle"), ("xlabel", "X Label"), ("ylabel", "Y Label")]:
        action = QAction(label, window)
        action.triggered.connect(lambda _checked=False, k=key: window.edit_axes_text(k))
        actions[key] = action

    tick_action = QAction("Tick Editor", window)
    tick_action.triggered.connect(window.show_tick_editor)
    actions["tick_editor"] = tick_action

    legend_action = QAction("Legend", window)
    legend_action.setCheckable(True)
    legend_action.triggered.connect(window.toggle_legend)
    actions["legend"] = legend_action

    grid_action = QAction("Grid", window)
    grid_action.setCheckable(True)
    grid_action.triggered.connect(window.toggle_grid)
    actions["grid"] = grid_action

    image_action = QAction("Image", window)
    image_action.triggered.connect(window.insert_image)
    actions["image"] = image_action

    for key, label in [
        ("line_plot", "Line Plot"), ("scatter_plot", "Scatter Plot"), ("bar_plot", "Bar Plot"),
        ("histogram", "Histogram"), ("heatmap", "Heatmap"),
    ]:
        action = QAction(label, window)
        action.triggered.connect(lambda _checked=False, k=key: window.insert_demo_plot(k))
        actions[key] = action

    subplots_action = QAction("Multiple Subplots", window)
    subplots_action.triggered.connect(window.show_subplots_dialog)
    actions["subplots"] = subplots_action

    export_action = QAction("Export", window)
    export_action.triggered.connect(window.show_export_dialog)
    actions["export"] = export_action

    return actions


def build_toolbar(window, actions: Dict[str, QAction]) -> QToolBar:
    """Build the classic, flat toolbar listing every action in spec order.

    Args:
        window: The owning main window (used as the toolbar's parent).
        actions: The action map returned by :func:`create_actions`.

    Returns:
        The populated, ready-to-add :class:`QToolBar`.
    """
    bar = QToolBar("Toolbar", window)
    bar.setObjectName("MainToolBar")
    bar.setMovable(True)
    order = [
        "select", "move", "zoom", "pan", "title", "subtitle", "xlabel", "ylabel", "tick_editor",
        "text", "annotation", "arrow", "rectangle", "ellipse", "line", "legend", "grid", "image",
        "line_plot", "scatter_plot", "bar_plot", "histogram", "heatmap", "subplots", "export",
    ]
    for key in order:
        bar.addAction(actions[key])
        if key in ("pan", "ylabel", "line", "grid", "heatmap"):
            bar.addSeparator()
    return bar
