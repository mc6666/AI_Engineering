"""The Object Tree dock widget: hierarchical view of the design document."""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMenu, QTreeWidget, QTreeWidgetItem, QWidget

from ..commands.property_change import PropertyChangeCommand
from ..models.axes_model import AxesModel
from ..models.figure_model import FigureModel

_ROLE_OBJECT = Qt.UserRole
_ROLE_CONTAINER = Qt.UserRole + 1


class ObjectTree(QTreeWidget):
    """Displays the Figure/Axes/Plots/Text/Shapes/Annotations hierarchy.

    Supports rename (double-click), delete, duplicate, hide/lock toggling
    from a context menu, and keeps its selection synchronized with the
    canvas selection.
    """

    def __init__(self, model: FigureModel, canvas, undo_manager, parent: Optional[QWidget] = None) -> None:
        """Initialize the tree for a given document and canvas.

        Args:
            model: The figure document to display.
            canvas: The :class:`~matplotlib_designer.designer.canvas.SceneCanvas`
                whose selection this tree stays in sync with.
            undo_manager: Shared undo/redo stack.
            parent: Optional Qt parent widget.
        """
        super().__init__(parent)
        self.model = model
        self.canvas = canvas
        self.undo_manager = undo_manager
        self.setHeaderHidden(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemChanged.connect(self._on_item_renamed)
        canvas.scene_changed.connect(self.refresh)
        canvas.selection_changed.connect(self._sync_from_canvas)
        self.refresh()

    def refresh(self) -> None:
        """Rebuild the whole tree from the current model state."""
        self.blockSignals(True)
        self.clear()
        root = QTreeWidgetItem([self.model.name])
        root.setData(0, _ROLE_OBJECT, self.model)
        self.addTopLevelItem(root)
        for axes in self.model.axes:
            self._add_axes_item(root, axes)
        self.expandAll()
        self.blockSignals(False)

    def _add_axes_item(self, parent_item: QTreeWidgetItem, axes: AxesModel) -> None:
        item = self._make_item(axes, axes.name)
        parent_item.addChild(item)
        groups = [("Plots", axes.plots), ("Text", axes.texts), ("Shapes", axes.shapes), ("Annotations", axes.annotations)]
        for label, objs in groups:
            if not objs:
                continue
            group_item = QTreeWidgetItem([f"{label} ({len(objs)})"])
            group_item.setFlags(group_item.flags() & ~Qt.ItemIsEditable)
            item.addChild(group_item)
            for obj in objs:
                group_item.addChild(self._make_item(obj, obj.name))

    def _make_item(self, obj, label: str) -> QTreeWidgetItem:
        item = QTreeWidgetItem([label])
        item.setData(0, _ROLE_OBJECT, obj)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        if getattr(obj, "locked", False):
            item.setForeground(0, Qt.gray)
        if not getattr(obj, "visible", True):
            font = item.font(0)
            font.setItalic(True)
            item.setFont(0, font)
        return item

    def _on_selection_changed(self) -> None:
        objs = [item.data(0, _ROLE_OBJECT) for item in self.selectedItems()]
        objs = [o for o in objs if not isinstance(o, FigureModel)]
        self.canvas.set_selection(objs)

    def _sync_from_canvas(self, objs: list) -> None:
        self.blockSignals(True)
        self.clearSelection()
        target_ids = {id(o) for o in objs}
        iterator = self.findItems("*", Qt.MatchWildcard | Qt.MatchRecursive)
        for item in iterator:
            obj = item.data(0, _ROLE_OBJECT)
            if obj is not None and id(obj) in target_ids:
                item.setSelected(True)
        self.blockSignals(False)

    def _on_item_renamed(self, item: QTreeWidgetItem, _column: int) -> None:
        obj = item.data(0, _ROLE_OBJECT)
        if obj is None or item.text(0) == getattr(obj, "name", None):
            return
        self.undo_manager.push(PropertyChangeCommand(obj, "name", item.text(0), self.canvas.on_scene_changed))

    def _show_context_menu(self, pos) -> None:
        item = self.itemAt(pos)
        if item is None:
            return
        obj = item.data(0, _ROLE_OBJECT)
        if obj is None or isinstance(obj, FigureModel):
            return
        menu = QMenu(self)
        rename_action = menu.addAction("Rename")
        duplicate_action = menu.addAction("Duplicate")
        delete_action = menu.addAction("Delete")
        menu.addSeparator()
        visible_action = menu.addAction("Hide" if obj.visible else "Show")
        lock_action = menu.addAction("Unlock" if obj.locked else "Lock")
        chosen = menu.exec(self.viewport().mapToGlobal(pos))
        if chosen == rename_action:
            self.editItem(item)
        elif chosen == duplicate_action:
            self._duplicate(obj)
        elif chosen == delete_action:
            self.canvas.set_selection([obj])
            self.canvas.delete_selection()
        elif chosen == visible_action:
            self.undo_manager.push(PropertyChangeCommand(obj, "visible", not obj.visible, self.canvas.on_scene_changed))
        elif chosen == lock_action:
            self.undo_manager.push(PropertyChangeCommand(obj, "locked", not obj.locked, self.canvas.on_scene_changed))

    def _duplicate(self, obj) -> None:
        """Deep-copy ``obj`` with a fresh id and add it via :meth:`SceneCanvas.add_clone`."""
        self.canvas.add_clone(obj)
