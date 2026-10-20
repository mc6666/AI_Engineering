"""The Property Inspector dock widget: edits the current selection's fields."""
from __future__ import annotations

from typing import Any, Callable, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..commands.property_change import PropertyChangeCommand
from ..models.annotation_model import AnnotationModel
from ..models.axes_model import AxesModel
from ..models.figure_model import FigureModel
from ..models.plot_model import PLOT_KINDS, PlotModel
from ..models.shape_model import ShapeModel
from ..models.text_model import TextModel
from ..widgets.color_button import ColorButton
from ..widgets.font_selector import FontSelector

LINE_STYLES = ["-", "--", "-.", ":", "None"]
ARROW_STYLES = ["-", "->", "-|>", "<->", "<|-|>", "fancy", "wedge"]
BOX_STYLES = ["none", "round", "square", "round4", "sawtooth"]
HA_OPTIONS = ["left", "center", "right"]
VA_OPTIONS = ["top", "center", "bottom"]
LEGEND_LOCS = ["best", "upper right", "upper left", "lower left", "lower right", "center"]


class PropertyPanel(QScrollArea):
    """Builds a property-editing form for whatever is currently selected."""

    def __init__(self, canvas, undo_manager, parent: Optional[QWidget] = None) -> None:
        """Initialize the panel and connect it to the canvas selection.

        Args:
            canvas: The :class:`~matplotlib_designer.designer.canvas.SceneCanvas`.
            undo_manager: Shared undo/redo stack.
            parent: Optional Qt parent widget.
        """
        super().__init__(parent)
        self.canvas = canvas
        self.undo_manager = undo_manager
        self.setWidgetResizable(True)
        self._body = QWidget()
        self._layout = QVBoxLayout(self._body)
        self._layout.setAlignment(Qt.AlignTop)
        self.setWidget(self._body)
        canvas.selection_changed.connect(self._rebuild)
        canvas.scene_changed.connect(self._rebuild)
        self._rebuild([])

    def _clear(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _rebuild(self, _selection: Optional[List[Any]] = None) -> None:
        self._clear()
        selection = self.canvas.selection
        if not selection:
            self._layout.addWidget(QLabel("No selection."))
            return
        obj = selection[0]
        form = QFormLayout()
        form.addRow(QLabel(f"<b>{type(obj).__name__}</b> — {obj.name}"))
        self._add_common_fields(form, obj)
        if isinstance(obj, TextModel):
            self._add_text_fields(form, obj)
        elif isinstance(obj, ShapeModel):
            self._add_shape_fields(form, obj)
        elif isinstance(obj, AnnotationModel):
            self._add_annotation_fields(form, obj)
        elif isinstance(obj, PlotModel):
            self._add_plot_fields(form, obj)
        elif isinstance(obj, AxesModel):
            self._add_axes_fields(form, obj)
        elif isinstance(obj, FigureModel):
            self._add_figure_fields(form, obj)
        container = QWidget()
        container.setLayout(form)
        self._layout.addWidget(container)
        if len(selection) > 1:
            self._layout.addWidget(QLabel(f"(+{len(selection) - 1} more selected, editing first only)"))

    # -- helpers -------------------------------------------------------- #
    def _push(self, obj: Any, attr: str, value: Any) -> None:
        self.undo_manager.push(PropertyChangeCommand(obj, attr, value, self.canvas.on_scene_changed))

    def _line_edit(self, form: QFormLayout, label: str, obj: Any, attr: str) -> None:
        edit = QLineEdit(str(getattr(obj, attr)))
        edit.editingFinished.connect(lambda: self._push(obj, attr, edit.text()))
        form.addRow(label, edit)

    def _double_spin(self, form: QFormLayout, label: str, obj: Any, attr: str, minimum=-1e6, maximum=1e6, step=0.01) -> None:
        spin = QDoubleSpinBox()
        spin.setRange(minimum, maximum)
        spin.setSingleStep(step)
        spin.setDecimals(3)
        spin.setValue(float(getattr(obj, attr)))
        spin.valueChanged.connect(lambda v: self._push(obj, attr, v))
        form.addRow(label, spin)

    def _int_spin(self, form: QFormLayout, label: str, obj: Any, attr: str, minimum=-999, maximum=999) -> None:
        spin = QSpinBox()
        spin.setRange(minimum, maximum)
        spin.setValue(int(getattr(obj, attr)))
        spin.valueChanged.connect(lambda v: self._push(obj, attr, v))
        form.addRow(label, spin)

    def _checkbox(self, form: QFormLayout, label: str, obj: Any, attr: str) -> None:
        box = QCheckBox()
        box.setChecked(bool(getattr(obj, attr)))
        box.toggled.connect(lambda v: self._push(obj, attr, v))
        form.addRow(label, box)

    def _combo(self, form: QFormLayout, label: str, obj: Any, attr: str, options: List[str]) -> None:
        combo = QComboBox()
        combo.addItems(options)
        current = str(getattr(obj, attr))
        if current in options:
            combo.setCurrentText(current)
        combo.currentTextChanged.connect(lambda v: self._push(obj, attr, v))
        form.addRow(label, combo)

    def _color(self, form: QFormLayout, label: str, obj: Any, attr: str, allow_none: bool = False) -> None:
        button = ColorButton(getattr(obj, attr), allow_none=allow_none)
        button.color_changed.connect(lambda v: self._push(obj, attr, v))
        form.addRow(label, button)

    def _font(self, form: QFormLayout, label: str, obj: Any, attr: str) -> None:
        selector = FontSelector(getattr(obj, attr))
        selector.currentTextChanged.connect(lambda v: self._push(obj, attr, v))
        form.addRow(label, selector)

    # -- field groups ----------------------------------------------------- #
    def _add_common_fields(self, form: QFormLayout, obj: Any) -> None:
        self._line_edit(form, "Name", obj, "name")
        self._checkbox(form, "Visible", obj, "visible")
        self._checkbox(form, "Locked", obj, "locked")
        self._double_spin(form, "Opacity", obj, "opacity", 0.0, 1.0, 0.05)
        self._int_spin(form, "Z-order", obj, "z_order")

    def _add_text_fields(self, form: QFormLayout, obj: TextModel) -> None:
        self._line_edit(form, "Content", obj, "content")
        self._font(form, "Font", obj, "font_family")
        self._double_spin(form, "Font Size", obj, "font_size", 1, 200, 0.5)
        self._checkbox(form, "Bold", obj, "bold")
        self._checkbox(form, "Italic", obj, "italic")
        self._checkbox(form, "Underline", obj, "underline")
        self._color(form, "Color", obj, "color")
        self._color(form, "Background", obj, "background", allow_none=True)
        self._combo(form, "Horiz. Align", obj, "ha", HA_OPTIONS)
        self._combo(form, "Vert. Align", obj, "va", VA_OPTIONS)
        self._double_spin(form, "Rotation", obj, "rotation", -360, 360, 1)
        self._double_spin(form, "X", obj, "x", 0, 1, 0.01)
        self._double_spin(form, "Y", obj, "y", 0, 1, 0.01)

    def _add_shape_fields(self, form: QFormLayout, obj: ShapeModel) -> None:
        self._double_spin(form, "X", obj, "x", -1, 2, 0.01)
        self._double_spin(form, "Y", obj, "y", -1, 2, 0.01)
        self._double_spin(form, "Width", obj, "width", 0.001, 2, 0.01)
        self._double_spin(form, "Height", obj, "height", 0.001, 2, 0.01)
        self._double_spin(form, "Rotation", obj, "rotation", -360, 360, 1)
        self._color(form, "Edge Color", obj, "edge_color")
        self._color(form, "Face Color", obj, "face_color")
        self._double_spin(form, "Line Width", obj, "line_width", 0, 20, 0.5)
        self._combo(form, "Line Style", obj, "line_style", LINE_STYLES)

    def _add_annotation_fields(self, form: QFormLayout, obj: AnnotationModel) -> None:
        self._line_edit(form, "Text", obj, "text")
        self._combo(form, "Arrow Style", obj, "arrow_style", ARROW_STYLES)
        self._combo(form, "Box Style", obj, "box_style", BOX_STYLES)
        self._color(form, "Face Color", obj, "face_color")
        self._color(form, "Edge Color", obj, "edge_color")
        self._double_spin(form, "Font Size", obj, "font_size", 1, 200, 0.5)

    def _add_plot_fields(self, form: QFormLayout, obj: PlotModel) -> None:
        self._combo(form, "Kind", obj, "kind", list(PLOT_KINDS))
        self._line_edit(form, "Label", obj, "label")
        self._color(form, "Color", obj, "color")
        self._combo(form, "Line Style", obj, "line_style", LINE_STYLES)
        self._double_spin(form, "Line Width", obj, "line_width", 0, 20, 0.5)
        self._line_edit(form, "Marker", obj, "marker")
        self._double_spin(form, "Marker Size", obj, "marker_size", 0, 100, 0.5)

    def _add_axes_fields(self, form: QFormLayout, obj: AxesModel) -> None:
        self._line_edit(form, "Title", obj.title, "content")
        self._line_edit(form, "X Label", obj.xlabel, "content")
        self._line_edit(form, "Y Label", obj.ylabel, "content")
        self._checkbox(form, "Show Grid", obj, "show_grid")
        self._checkbox(form, "Show Legend", obj, "show_legend")
        self._combo(form, "Legend Loc", obj, "legend_loc", LEGEND_LOCS)
        self._color(form, "Background", obj, "facecolor")
        left, bottom, width, height = obj.position
        self._position_row(form, "Position", obj, ("left", left), ("bottom", bottom), ("width", width), ("height", height))

    def _position_row(self, form: QFormLayout, label: str, obj: AxesModel, *fields) -> None:
        names = [f[0] for f in fields]

        def make_setter(index: int) -> Callable[[float], None]:
            def setter(value: float) -> None:
                pos = list(obj.position)
                pos[index] = value
                self._push(obj, "position", tuple(pos))
            return setter

        row = QWidget()
        from PySide6.QtWidgets import QHBoxLayout

        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        for index, (_name, value) in enumerate(fields):
            spin = QDoubleSpinBox()
            spin.setRange(-1, 2)
            spin.setSingleStep(0.01)
            spin.setDecimals(3)
            spin.setValue(value)
            spin.valueChanged.connect(make_setter(index))
            row_layout.addWidget(spin)
        form.addRow(label, row)

    def _add_figure_fields(self, form: QFormLayout, obj: FigureModel) -> None:
        self._double_spin(form, "Width (in)", obj, "width_in", 1, 100, 0.1)
        self._double_spin(form, "Height (in)", obj, "height_in", 1, 100, 0.1)
        self._int_spin(form, "DPI", obj, "dpi", 10, 1200)
        self._color(form, "Background", obj, "facecolor")
        self._combo(form, "Layout", obj, "layout", ["none", "tight", "constrained"])
        self._line_edit(form, "Suptitle", obj, "suptitle")
