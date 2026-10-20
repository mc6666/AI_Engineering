"""The application's main window: menus, docks, and top-level orchestration."""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QInputDialog,
    QMainWindow,
    QMessageBox,
)

from ..commands.add_axes import AddAxesCommand
from ..commands.add_plot import AddPlotCommand
from ..commands.property_change import PropertyChangeCommand
from ..commands.undo import UndoManager
from ..dialogs.export_dialog import ExportDialog
from ..dialogs.new_figure_dialog import NewFigureDialog
from ..dialogs.subplots_dialog import SubplotsDialog
from ..export.image_export import export_image
from ..export.pickle_export import export_pickle
from ..export.script_export import export_script
from ..models.axes_model import AxesModel
from ..models.figure_model import FigureModel
from ..models.plot_model import PlotModel
from ..plugins.loader import load_plugins
from ..serialization.project_serializer import load_project, save_project
from .canvas import SceneCanvas
from .object_tree import ObjectTree
from .property_panel import PropertyPanel
from .ribbon import build_ribbon
from .statusbar import DesignerStatusBar
from .toolbar import build_toolbar, create_actions

_THEMES_DIR = Path(__file__).resolve().parent.parent / "resources" / "themes"
_PLUGINS_DIR = Path(__file__).resolve().parent.parent / "plugins" / "installed"

#: Demo data used to seed a plot when the user clicks a plot-type button,
#: since the visual designer creates plots before any data is loaded.
import numpy as _np

_DEMO_X = list(_np.linspace(0, 10, 30))
_DEMO_Y = list(_np.sin(_np.linspace(0, 10, 30)) * 5 + 5)
_DEMO_Z = [list(row) for row in _np.random.default_rng(0).random((10, 10))]


class MainWindow(QMainWindow):
    """Top-level window wiring the canvas, docks, menus and toolbar together."""

    def __init__(self) -> None:
        """Build a new window around a fresh, single-axes document."""
        super().__init__()
        self.setWindowTitle("Matplotlib Designer V2")
        self.resize(1400, 900)

        self.model = FigureModel.new_default()
        self.undo_manager = UndoManager()
        self.current_path: Optional[Path] = None
        self._clipboard = None

        self.canvas = SceneCanvas(self.model, self.undo_manager)
        self.setCentralWidget(self.canvas)

        self.object_tree = ObjectTree(self.model, self.canvas, self.undo_manager)
        self.property_panel = PropertyPanel(self.canvas, self.undo_manager)
        self._add_dock("Object Tree", self.object_tree, Qt.LeftDockWidgetArea)
        self._add_dock("Properties", self.property_panel, Qt.RightDockWidgetArea)

        self.status_bar = DesignerStatusBar(self.canvas, self.undo_manager)
        self.setStatusBar(self.status_bar)

        self.actions_map = create_actions(self)
        self.addToolBar(Qt.TopToolBarArea, build_toolbar(self, self.actions_map))
        self.addToolBarBreak()
        ribbon_bar = self.addToolBar("Ribbon")
        ribbon_bar.setObjectName("RibbonBar")
        ribbon_bar.setMovable(False)
        ribbon_bar.addWidget(build_ribbon(self, self.actions_map))

        self._build_menus()
        self.apply_theme("light")
        load_plugins(_PLUGINS_DIR, self)

    # ------------------------------------------------------------------ #
    # Construction helpers
    # ------------------------------------------------------------------ #
    def _add_dock(self, title: str, widget, area: Qt.DockWidgetArea) -> QDockWidget:
        dock = QDockWidget(title, self)
        dock.setObjectName(title.replace(" ", ""))
        dock.setWidget(widget)
        dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.addDockWidget(area, dock)
        return dock

    def _build_menus(self) -> None:
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        self._add(file_menu, "&New", self.new_project, QKeySequence.New)
        self._add(file_menu, "&Open...", self.open_project, QKeySequence.Open)
        self._add(file_menu, "&Save", self.save_project, QKeySequence.Save)
        self._add(file_menu, "Save &As...", self.save_project_as)
        file_menu.addSeparator()
        self._add(file_menu, "&Export...", self.show_export_dialog)
        file_menu.addSeparator()
        self._add(file_menu, "E&xit", self.close, QKeySequence.Quit)

        edit_menu = menu_bar.addMenu("&Edit")
        self._add(edit_menu, "&Undo", self.undo_manager.undo, QKeySequence.Undo)
        self._add(edit_menu, "&Redo", self.undo_manager.redo, QKeySequence.Redo)
        edit_menu.addSeparator()
        self._add(edit_menu, "Cu&t", self.cut_selection, QKeySequence.Cut)
        self._add(edit_menu, "&Copy", self.copy_selection, QKeySequence.Copy)
        self._add(edit_menu, "&Paste", self.paste_clipboard, QKeySequence.Paste)
        self._add(edit_menu, "D&uplicate", self.duplicate_selection, "Ctrl+D")
        self._add(edit_menu, "&Delete", self.canvas.delete_selection, QKeySequence.Delete)

        view_menu = menu_bar.addMenu("&View")
        for dock in self.findChildren(QDockWidget):
            view_menu.addAction(dock.toggleViewAction())
        theme_menu = view_menu.addMenu("Theme")
        for theme in ["light", "dark", "scientific", "nature", "ieee", "presentation"]:
            self._add(theme_menu, theme.title(), lambda _checked=False, t=theme: self.apply_theme(t))

        insert_menu = menu_bar.addMenu("&Insert")
        for key in ["text", "annotation", "arrow", "rectangle", "ellipse", "line", "image"]:
            insert_menu.addAction(self.actions_map[key])
        self._add(insert_menu, "New Axes", self.insert_axes)

        plot_menu = menu_bar.addMenu("&Plot")
        for key in ["line_plot", "scatter_plot", "bar_plot", "histogram", "heatmap"]:
            plot_menu.addAction(self.actions_map[key])

        layout_menu = menu_bar.addMenu("&Layout")
        self._add(layout_menu, "Tight Layout", lambda: self.set_layout_mode("tight"))
        self._add(layout_menu, "Constrained Layout", lambda: self.set_layout_mode("constrained"))
        self._add(layout_menu, "No Layout Engine", lambda: self.set_layout_mode("none"))
        layout_menu.addAction(self.actions_map["subplots"])

        window_menu = menu_bar.addMenu("&Window")
        self._add(window_menu, "Reset Dock Layout", self.reset_dock_layout)

        help_menu = menu_bar.addMenu("&Help")
        self._add(help_menu, "About Matplotlib Designer", self.show_about)

    def _add(self, menu, label: str, slot, shortcut=None) -> QAction:
        action = QAction(label, self)
        if shortcut is not None:
            action.setShortcut(shortcut)
        action.triggered.connect(slot)
        menu.addAction(action)
        return action

    # ------------------------------------------------------------------ #
    # File menu
    # ------------------------------------------------------------------ #
    def new_project(self) -> None:
        """Prompt for figure size/DPI/background and start a fresh document."""
        dialog = NewFigureDialog(self)
        if dialog.exec():
            width, height, dpi, color = dialog.values()
            self.model = FigureModel.new_default()
            self.model.width_in, self.model.height_in, self.model.dpi, self.model.facecolor = width, height, dpi, color
            self._replace_document(self.model)
            self.current_path = None

    def open_project(self) -> None:
        """Open a previously saved ``.json`` project file."""
        path, _ = QFileDialog.getOpenFileName(self, "Open Project", "", "Matplotlib Designer Project (*.json)")
        if not path:
            return
        try:
            self.model = load_project(path)
        except Exception as exc:
            QMessageBox.critical(self, "Open Failed", str(exc))
            return
        self._replace_document(self.model)
        self.current_path = Path(path)

    def save_project(self) -> None:
        """Save to the current path, or prompt for one if there isn't one yet."""
        if self.current_path is None:
            self.save_project_as()
            return
        save_project(self.model, self.current_path)
        self.status_bar.showMessage(f"Saved to {self.current_path}", 3000)

    def save_project_as(self) -> None:
        """Prompt for a destination and save the project there."""
        path, _ = QFileDialog.getSaveFileName(self, "Save Project As", "", "Matplotlib Designer Project (*.json)")
        if not path:
            return
        self.current_path = Path(path)
        self.save_project()

    def show_export_dialog(self) -> None:
        """Prompt for an export destination/format and export the figure."""
        result = ExportDialog.get_export_path(self)
        if result is None:
            return
        path, fmt = result
        try:
            if fmt == "json":
                save_project(self.model, path)
            elif fmt == "py":
                export_script(self.model, path)
            elif fmt == "pickle":
                export_pickle(self.canvas, path)
            else:
                export_image(self.canvas, path, fmt)
            self.status_bar.showMessage(f"Exported to {path}", 3000)
        except Exception as exc:
            QMessageBox.critical(self, "Export Failed", str(exc))

    def _replace_document(self, model: FigureModel) -> None:
        self.model = model
        self.canvas.model = model
        self.undo_manager.clear()
        self.canvas.set_selection([])
        self.object_tree.model = model
        self.canvas.on_scene_changed()

    # ------------------------------------------------------------------ #
    # Edit menu
    # ------------------------------------------------------------------ #
    def copy_selection(self) -> None:
        """Deep-copy the current selection to an in-memory clipboard."""
        if self.canvas.selection:
            self._clipboard = [copy.deepcopy(obj) for obj in self.canvas.selection]

    def cut_selection(self) -> None:
        """Copy then delete the current selection."""
        self.copy_selection()
        self.canvas.delete_selection()

    def paste_clipboard(self) -> None:
        """Re-add clones of whatever was last copied."""
        if not self._clipboard:
            return
        for obj in self._clipboard:
            self.canvas.add_clone(obj)

    def duplicate_selection(self) -> None:
        """Duplicate every selected object in place."""
        for obj in list(self.canvas.selection):
            self.canvas.add_clone(obj)

    # ------------------------------------------------------------------ #
    # Tool / insert / plot callbacks (used by toolbar.py's actions)
    # ------------------------------------------------------------------ #
    def set_active_tool(self, name: str) -> None:
        """Activate a canvas tool and reflect it in the status bar.

        Args:
            name: Tool key, see :data:`matplotlib_designer.designer.canvas.TOOL_CLASSES`.
        """
        self.canvas.set_active_tool(name)
        self.status_bar.set_tool(name.title())

    def current_axes(self) -> Optional[AxesModel]:
        """Return a reasonable "current" axes: from selection, else the first one."""
        for obj in self.canvas.selection:
            if isinstance(obj, AxesModel):
                return obj
            owner = self.canvas.object_axes(obj)
            if owner is not None:
                return owner
        return self.model.axes[0] if self.model.axes else None

    def edit_axes_text(self, key: str) -> None:
        """Prompt for and apply new title/subtitle/xlabel/ylabel text.

        Args:
            key: One of ``"title"``, ``"subtitle"``, ``"xlabel"``, ``"ylabel"``.
        """
        axes = self.current_axes()
        if axes is None:
            return
        target = axes.title if key in ("title", "subtitle") else (axes.xlabel if key == "xlabel" else axes.ylabel)
        text, ok = QInputDialog.getText(self, key.title(), "Text:", text=target.content)
        if ok:
            self.undo_manager.push(PropertyChangeCommand(target, "content", text, self.canvas.on_scene_changed))

    def show_tick_editor(self) -> None:
        """Placeholder tick-label editor: toggles the grid as a stand-in control."""
        axes = self.current_axes()
        if axes is None:
            return
        QMessageBox.information(
            self, "Tick Editor",
            "Full tick-format editing is not yet implemented in this build; "
            "use the Property Inspector to adjust grid/legend for now.",
        )

    def toggle_legend(self, checked: bool) -> None:
        """Toggle whether the current axes shows a legend."""
        axes = self.current_axes()
        if axes is not None:
            self.undo_manager.push(PropertyChangeCommand(axes, "show_legend", checked, self.canvas.on_scene_changed))

    def toggle_grid(self, checked: bool) -> None:
        """Toggle whether the current axes shows a grid."""
        axes = self.current_axes()
        if axes is not None:
            self.undo_manager.push(PropertyChangeCommand(axes, "show_grid", checked, self.canvas.on_scene_changed))

    def insert_image(self) -> None:
        """Insert an image file as an ``imshow`` plot in the current axes."""
        path, _ = QFileDialog.getOpenFileName(self, "Insert Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not path:
            return
        axes = self._axes_for_insert()
        try:
            import matplotlib.image as mpimg

            data = mpimg.imread(path)
        except Exception as exc:
            QMessageBox.critical(self, "Insert Image Failed", str(exc))
            return
        plot = PlotModel(name="Image", kind="image", z=data.tolist() if hasattr(data, "tolist") else list(data))
        self.undo_manager.push(AddPlotCommand(axes, plot, self.canvas.on_scene_changed))

    def insert_demo_plot(self, key: str) -> None:
        """Add a demo-data plot of the requested kind to the current axes.

        Args:
            key: One of ``"line_plot"``, ``"scatter_plot"``, ``"bar_plot"``,
                ``"histogram"``, ``"heatmap"``.
        """
        kind_map = {
            "line_plot": "line", "scatter_plot": "scatter", "bar_plot": "bar",
            "histogram": "hist", "heatmap": "heatmap",
        }
        kind = kind_map[key]
        axes = self._axes_for_insert()
        if kind == "heatmap":
            plot = PlotModel(name="Heatmap", kind=kind, z=_DEMO_Z)
        else:
            plot = PlotModel(name=key.replace("_", " ").title(), kind=kind, x=_DEMO_X, y=_DEMO_Y, label=key)
        self.undo_manager.push(AddPlotCommand(axes, plot, self.canvas.on_scene_changed))

    def _axes_for_insert(self) -> AxesModel:
        axes = self.current_axes()
        if axes is None:
            axes = AxesModel(name=f"Axes {len(self.model.axes) + 1}")
            self.undo_manager.push(AddAxesCommand(self.model, axes, self.canvas.on_scene_changed))
        return axes

    def insert_axes(self) -> None:
        """Add a new default-positioned axes to the figure."""
        axes = AxesModel(name=f"Axes {len(self.model.axes) + 1}")
        self.undo_manager.push(AddAxesCommand(self.model, axes, self.canvas.on_scene_changed))

    def show_subplots_dialog(self) -> None:
        """Prompt for a rows x cols grid and replace the figure's axes with it."""
        dialog = SubplotsDialog(self)
        if not dialog.exec():
            return
        rows, cols = dialog.values()
        from ..commands.redo import MacroCommand
        from ..commands.delete import DeleteObjectCommand

        delete_commands = [DeleteObjectCommand(self.model.axes, ax, self.canvas.on_scene_changed) for ax in list(self.model.axes)]
        margin, gap = 0.08, 0.06
        cell_w = (1 - 2 * margin - gap * (cols - 1)) / cols
        cell_h = (1 - 2 * margin - gap * (rows - 1)) / rows
        add_commands = []
        index = 1
        for row in range(rows):
            for col in range(cols):
                left = margin + col * (cell_w + gap)
                bottom = margin + (rows - row - 1) * (cell_h + gap)
                axes = AxesModel(name=f"Axes {index}", position=(left, bottom, cell_w, cell_h))
                add_commands.append(AddAxesCommand(self.model, axes, self.canvas.on_scene_changed))
                index += 1
        self.undo_manager.push(MacroCommand(delete_commands + add_commands, label="Multiple Subplots"))

    def set_layout_mode(self, mode: str) -> None:
        """Set the figure's layout engine (``"none"``, ``"tight"``, ``"constrained"``)."""
        self.undo_manager.push(PropertyChangeCommand(self.model, "layout", mode, self.canvas.on_scene_changed))

    # ------------------------------------------------------------------ #
    # View menu / themes / window
    # ------------------------------------------------------------------ #
    def apply_theme(self, theme: str) -> None:
        """Load and apply a ``.qss`` stylesheet by theme name.

        Args:
            theme: One of ``"light"``, ``"dark"``, ``"scientific"``,
                ``"nature"``, ``"ieee"``, ``"presentation"``.
        """
        path = _THEMES_DIR / f"{theme}.qss"
        if path.is_file():
            self.setStyleSheet(path.read_text(encoding="utf-8"))

    def reset_dock_layout(self) -> None:
        """Restore the default dock widget arrangement."""
        for dock in self.findChildren(QDockWidget):
            dock.setFloating(False)
            dock.show()

    def show_about(self) -> None:
        """Show the About dialog."""
        QMessageBox.about(
            self, "About Matplotlib Designer",
            "Matplotlib Designer V2\n\nA visual editor for native Matplotlib figures.",
        )

    # ------------------------------------------------------------------ #
    # Extensibility hooks used by plugins
    # ------------------------------------------------------------------ #
    def add_menu_action(self, menu_name: str, label: str, slot) -> QAction:
        """Add an action to a top-level menu by name, creating it if needed.

        Args:
            menu_name: Menu title, e.g. ``"Plot"``.
            label: Action label.
            slot: Callable invoked when the action triggers.

        Returns:
            The created :class:`QAction`.
        """
        for action in self.menuBar().actions():
            if action.text().replace("&", "") == menu_name:
                return self._add(action.menu(), label, slot)
        menu = self.menuBar().addMenu(menu_name)
        return self._add(menu, label, slot)

    def add_dock_widget(self, title: str, widget, area: Qt.DockWidgetArea = Qt.RightDockWidgetArea) -> QDockWidget:
        """Add a new dock widget, e.g. contributed by a plugin.

        Args:
            title: Dock title.
            widget: The widget to host inside the dock.
            area: Initial dock area.

        Returns:
            The created :class:`QDockWidget`.
        """
        return self._add_dock(title, widget, area)
