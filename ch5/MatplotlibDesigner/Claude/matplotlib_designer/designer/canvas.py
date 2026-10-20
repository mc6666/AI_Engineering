"""The interactive Matplotlib canvas: rendering, selection, drag and resize.

This module owns the single source of truth for how a
:class:`~matplotlib_designer.models.figure_model.FigureModel` is turned into
a live :class:`matplotlib.figure.Figure`, and how mouse interaction on that
figure is translated back into model mutations (wrapped in undoable
commands).

Coordinate convention
    Every scene object's geometry is stored in *axes-fraction* coordinates
    (0-1 relative to its owning axes), except an axes' own ``position``,
    which is stored in *figure-fraction* coordinates, exactly like
    :meth:`matplotlib.figure.Figure.add_axes`. All hit-testing, dragging and
    selection-overlay drawing is done in figure-fraction space so it stays
    correct regardless of DPI or window size; a small set of module-level
    helper functions convert between the two spaces.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import Ellipse, Rectangle
from matplotlib.lines import Line2D
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QInputDialog, QVBoxLayout, QWidget

from ..commands.move import MoveObjectCommand
from ..commands.property_change import PropertyChangeCommand
from ..commands.redo import MacroCommand
from ..commands.resize import ResizeObjectCommand
from ..commands.undo import UndoManager
from ..models.annotation_model import AnnotationModel
from ..models.axes_model import AxesModel
from ..models.figure_model import FigureModel
from ..models.plot_model import PlotModel
from ..models.shape_model import ShapeModel
from ..models.text_model import TextModel
from ..tools.base_tool import ToolContext
from ..tools.select_tool import SelectTool
from ..tools.text_tool import TextTool
from ..tools.arrow_tool import ArrowTool
from ..tools.annotation_tool import AnnotationTool
from ..tools.rectangle_tool import RectangleTool
from ..tools.ellipse_tool import EllipseTool
from ..tools.line_tool import LineTool
from ..tools.zoom_tool import ZoomTool
from ..tools.pan_tool import PanTool

#: Fixed on-screen (figure-fraction) half-size of the hit/selection box drawn
#: around anchor-point objects (text, annotations) whose true rendered
#: extent we do not query from the renderer.
TEXT_HIT_HALF_W = 0.06
TEXT_HIT_HALF_H = 0.025
#: Figure-fraction tolerance for clicking a resize handle.
HANDLE_TOLERANCE = 0.012


def axes_to_fig_point(axes_pos: Tuple[float, float, float, float], point: Tuple[float, float]) -> Tuple[float, float]:
    """Convert an axes-fraction point to a figure-fraction point."""
    left, bottom, width, height = axes_pos
    x, y = point
    return (left + x * width, bottom + y * height)


def fig_to_axes_point(axes_pos: Tuple[float, float, float, float], point: Tuple[float, float]) -> Tuple[float, float]:
    """Convert a figure-fraction point to an axes-fraction point."""
    left, bottom, width, height = axes_pos
    x, y = point
    return ((x - left) / width, (y - bottom) / height)


def axes_to_fig_rect(
    axes_pos: Tuple[float, float, float, float], rect: Tuple[float, float, float, float]
) -> Tuple[float, float, float, float]:
    """Convert an axes-fraction rect to a figure-fraction rect."""
    left, bottom, width, height = axes_pos
    x, y, rw, rh = rect
    return (left + x * width, bottom + y * height, rw * width, rh * height)


def _text_hit_rect(anchor: Tuple[float, float], ha: str, va: str) -> Tuple[float, float, float, float]:
    """Build a fixed-size figure-fraction hit box for an anchored text point."""
    x, y = anchor
    x0 = x if ha == "left" else (x - TEXT_HIT_HALF_W if ha == "right" else x - TEXT_HIT_HALF_W)
    y0 = y if va == "bottom" else (y - 2 * TEXT_HIT_HALF_H if va == "top" else y - TEXT_HIT_HALF_H)
    return (x0, y0, TEXT_HIT_HALF_W * 2, TEXT_HIT_HALF_H * 2)


def _point_in_rect(px: float, py: float, rect: Tuple[float, float, float, float]) -> bool:
    x, y, w, h = rect
    return x <= px <= x + w and y <= py <= y + h


TOOL_CLASSES = {
    "select": SelectTool,
    "text": TextTool,
    "arrow": ArrowTool,
    "annotation": AnnotationTool,
    "rectangle": RectangleTool,
    "ellipse": EllipseTool,
    "line": LineTool,
    "zoom": ZoomTool,
    "pan": PanTool,
}


class SceneCanvas(QWidget):
    """Embeds a live-rendered figure in a Qt widget and drives all interaction.

    Attributes:
        selection_changed: Emitted with the new selection list whenever it changes.
        scene_changed: Emitted after any structural or property change.
    """

    selection_changed = Signal(list)
    scene_changed = Signal()

    def __init__(self, model: FigureModel, undo_manager: UndoManager, parent: Optional[QWidget] = None) -> None:
        """Initialize the canvas for a given document.

        Args:
            model: The figure document to render and edit.
            undo_manager: Shared undo/redo stack used by every tool.
            parent: Optional Qt parent widget.
        """
        super().__init__(parent)
        matplotlib.rcParams["figure.autolayout"] = False
        self.model = model
        self.undo_manager = undo_manager
        self._selection: List[object] = []
        self._parent_axes: Dict[int, AxesModel] = {}
        self._tools = {name: cls() for name, cls in TOOL_CLASSES.items()}
        self._active_tool_name = "select"
        self._preview_patch = None
        self._rubber_band_start: Optional[Tuple[float, float]] = None
        self._dragging = False

        self.figure: Figure = Figure()
        self.mpl_canvas = FigureCanvasQTAgg(self.figure)
        self.mpl_canvas.setFocusPolicy(Qt.StrongFocus)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.mpl_canvas)

        self.mpl_canvas.mpl_connect("button_press_event", self._on_press)
        self.mpl_canvas.mpl_connect("motion_notify_event", self._on_move)
        self.mpl_canvas.mpl_connect("button_release_event", self._on_release)
        self.mpl_canvas.mpl_connect("scroll_event", self._on_scroll)

        self.rebuild()

    # ------------------------------------------------------------------ #
    # Tool management
    # ------------------------------------------------------------------ #
    def set_active_tool(self, name: str) -> None:
        """Switch the active interaction tool.

        Args:
            name: One of the keys in :data:`TOOL_CLASSES`.
        """
        if name not in self._tools:
            return
        self._tools[self._active_tool_name].deactivate(self)
        self._active_tool_name = name

    @property
    def active_tool_name(self) -> str:
        """Name of the currently active tool."""
        return self._active_tool_name

    # ------------------------------------------------------------------ #
    # Rendering
    # ------------------------------------------------------------------ #
    def on_scene_changed(self) -> None:
        """Rebuild the figure and notify listeners after a scene mutation."""
        self.rebuild()
        self.scene_changed.emit()

    def rebuild(self) -> None:
        """Rebuild the entire Matplotlib figure from :attr:`model`.

        This is intentionally a full rebuild rather than an incremental
        patch: it is far simpler to reason about and, at the object counts
        this application targets, fast enough not to be noticeable.
        """
        m = self.model
        self.figure.clear()
        self.figure.set_size_inches(m.width_in, m.height_in)
        self.figure.set_dpi(m.dpi)
        self.figure.set_facecolor(m.facecolor)
        if m.suptitle:
            self.figure.suptitle(m.suptitle)

        self._parent_axes = {}
        for axes_model in m.axes:
            self._build_axes(axes_model)

        if m.layout == "tight":
            try:
                self.figure.tight_layout()
            except Exception:
                pass

        self._overlay_ax = self.figure.add_axes((0, 0, 1, 1))
        self._overlay_ax.set_axis_off()
        self._overlay_ax.patch.set_alpha(0.0)
        self._overlay_ax.set_xlim(0, 1)
        self._overlay_ax.set_ylim(0, 1)
        self._draw_selection_overlay()
        self.mpl_canvas.draw_idle()

    def draw_idle(self) -> None:
        """Redraw only the selection overlay, without rebuilding the figure."""
        self._draw_selection_overlay()
        self.mpl_canvas.draw_idle()

    def _build_axes(self, axes_model: AxesModel) -> None:
        """Create one Matplotlib Axes (and its children) from an :class:`AxesModel`."""
        projection = None if axes_model.projection == "rectilinear" else axes_model.projection
        ax = self.figure.add_axes(list(axes_model.position), projection=projection)
        ax.set_facecolor(axes_model.facecolor)
        ax.grid(axes_model.show_grid)

        if axes_model.title.content:
            t = ax.set_title(axes_model.title.content, fontsize=axes_model.title.font_size,
                              fontweight=axes_model.title.font_weight, color=axes_model.title.color)
            t.set_position((axes_model.title.x, axes_model.title.y))
        if axes_model.xlabel.content:
            ax.set_xlabel(axes_model.xlabel.content, fontsize=axes_model.xlabel.font_size,
                           fontweight=axes_model.xlabel.font_weight, color=axes_model.xlabel.color)
        if axes_model.ylabel.content:
            ax.set_ylabel(axes_model.ylabel.content, fontsize=axes_model.ylabel.font_size,
                           fontweight=axes_model.ylabel.font_weight, color=axes_model.ylabel.color)

        for plot in axes_model.plots:
            self._parent_axes[id(plot)] = axes_model
            self._add_plot(ax, plot)
        if axes_model.show_legend and any(p.label for p in axes_model.plots):
            ax.legend(loc=axes_model.legend_loc)

        for shape in axes_model.shapes:
            self._parent_axes[id(shape)] = axes_model
            self._add_shape(ax, shape)
        for text in axes_model.texts:
            self._parent_axes[id(text)] = axes_model
            self._add_text(ax, text)
        for annotation in axes_model.annotations:
            self._parent_axes[id(annotation)] = axes_model
            self._add_annotation(ax, annotation)

    def _add_plot(self, ax, plot: PlotModel) -> None:
        """Draw a single :class:`PlotModel` series using the right Matplotlib call."""
        kind = plot.kind
        kwargs = dict(color=plot.color, label=plot.label or None)
        try:
            if kind == "line":
                ax.plot(plot.x, plot.y, linestyle=plot.line_style, linewidth=plot.line_width,
                        marker=plot.marker or None, markersize=plot.marker_size, **kwargs)
            elif kind == "scatter":
                ax.scatter(plot.x, plot.y, s=plot.marker_size ** 1.6, **kwargs)
            elif kind == "bar":
                ax.bar(plot.x, plot.y, **kwargs)
            elif kind == "barh":
                ax.barh(plot.x, plot.y, **kwargs)
            elif kind == "hist":
                ax.hist(plot.y or plot.x, **kwargs)
            elif kind == "pie":
                ax.pie(plot.y or plot.x, labels=None)
            elif kind == "box":
                ax.boxplot([plot.y] if plot.y else [plot.x])
            elif kind == "violin":
                ax.violinplot([plot.y] if plot.y else [plot.x])
            elif kind == "stem":
                ax.stem(plot.x, plot.y)
            elif kind == "step":
                ax.step(plot.x, plot.y, **kwargs)
            elif kind == "heatmap" and plot.z is not None:
                ax.imshow(plot.z, cmap=plot.colormap, aspect="auto")
            elif kind == "contour" and plot.z is not None:
                ax.contour(plot.z, cmap=plot.colormap)
            elif kind == "image" and plot.z is not None:
                ax.imshow(plot.z, cmap=plot.colormap)
            elif kind == "errorbar":
                ax.errorbar(plot.x, plot.y, yerr=plot.yerr, **kwargs)
            elif kind == "stack":
                ax.stackplot(plot.x, plot.y, colors=[plot.color])
            elif kind == "area":
                ax.fill_between(plot.x, plot.y, color=plot.color, alpha=0.5, label=plot.label or None)
        except Exception:
            # Malformed/incomplete demo data should never crash the editor.
            pass

    def _add_shape(self, ax, shape: ShapeModel) -> None:
        """Add a Matplotlib patch for a :class:`ShapeModel`, in axes-fraction space."""
        style = dict(
            edgecolor=shape.edge_color, facecolor=shape.face_color,
            linewidth=shape.line_width, linestyle=shape.line_style,
            transform=ax.transAxes, clip_on=False, alpha=shape.opacity,
            zorder=5 + shape.z_order,
        )
        if not shape.visible:
            return
        if shape.kind == "rectangle":
            patch = Rectangle((shape.x, shape.y), shape.width, shape.height, angle=shape.rotation, **style)
            ax.add_patch(patch)
        elif shape.kind in ("ellipse", "circle"):
            cx, cy = shape.x + shape.width / 2, shape.y + shape.height / 2
            patch = Ellipse((cx, cy), shape.width, shape.height, angle=shape.rotation, **style)
            ax.add_patch(patch)
        elif shape.kind in ("line", "polygon", "bezier", "freehand") and shape.points:
            xs = [p[0] for p in shape.points]
            ys = [p[1] for p in shape.points]
            line = Line2D(xs, ys, color=shape.edge_color, linewidth=shape.line_width,
                           linestyle=shape.line_style, transform=ax.transAxes, alpha=shape.opacity)
            ax.add_line(line)

    def _add_text(self, ax, text: TextModel) -> None:
        """Add a Matplotlib ``Text`` artist for a :class:`TextModel`."""
        if not text.visible:
            return
        bbox = None if text.background == "none" else dict(facecolor=text.background, edgecolor="none")
        ax.text(
            text.x, text.y, text.content, transform=ax.transAxes,
            ha=text.ha, va=text.va, rotation=text.rotation, color=text.color,
            fontsize=text.font_size, fontweight=text.font_weight, fontstyle=text.font_style,
            family=text.font_family, bbox=bbox, alpha=text.opacity, usetex=text.use_tex,
            wrap=text.wrap, zorder=6 + text.z_order,
        )

    def _add_annotation(self, ax, annotation: AnnotationModel) -> None:
        """Add a Matplotlib ``annotate`` callout for an :class:`AnnotationModel`."""
        if not annotation.visible:
            return
        arrowprops = dict(arrowstyle=annotation.arrow_style, color=annotation.edge_color) if annotation.arrow_style else None
        bbox = None
        if annotation.box_style != "none":
            bbox = dict(boxstyle=annotation.box_style, fc=annotation.face_color, ec=annotation.edge_color)
        ax.annotate(
            annotation.text, xy=(annotation.x, annotation.y), xytext=(annotation.xtext, annotation.ytext),
            xycoords="axes fraction", textcoords="axes fraction",
            arrowprops=arrowprops, bbox=bbox, fontsize=annotation.font_size, alpha=annotation.opacity,
            zorder=7 + annotation.z_order,
        )

    # ------------------------------------------------------------------ #
    # Selection
    # ------------------------------------------------------------------ #
    @property
    def selection(self) -> List[object]:
        """The current multi-selection, as a list of model objects."""
        return self._selection

    def set_selection(self, objs: List[object]) -> None:
        """Replace the current selection.

        Args:
            objs: New selection list.
        """
        self._selection = list(objs)
        self.selection_changed.emit(self._selection)
        self.draw_idle()

    def toggle_selection(self, obj: object) -> None:
        """Add or remove ``obj`` from the current selection.

        Args:
            obj: The object to toggle.
        """
        if obj in self._selection:
            self._selection.remove(obj)
        else:
            self._selection.append(obj)
        self.selection_changed.emit(self._selection)
        self.draw_idle()

    def get_selection_handles(self, obj: object) -> List[str]:
        """Return the resize-handle names available for ``obj``.

        Only axes and box-shaped shapes (rectangle/ellipse/circle) expose
        resize handles; text, annotations and lines are move-only.

        Args:
            obj: The object to query.

        Returns:
            A list of handle codes such as ``"nw"``, ``"se"``, ``"e"``.
        """
        if isinstance(obj, AxesModel):
            return ["nw", "n", "ne", "e", "se", "s", "sw", "w"]
        if isinstance(obj, ShapeModel) and obj.kind in ("rectangle", "ellipse", "circle"):
            return ["nw", "n", "ne", "e", "se", "s", "sw", "w"]
        return []

    def hit_test_handle(self, fx: float, fy: float) -> Optional[str]:
        """Return the resize handle at figure-fraction point ``(fx, fy)``, if any."""
        if len(self._selection) != 1:
            return None
        obj = self._selection[0]
        handles = self.get_selection_handles(obj)
        if not handles:
            return None
        rect = self.get_object_rect(obj)
        if rect is None:
            return None
        x, y, w, h = rect
        anchors = {
            "sw": (x, y), "s": (x + w / 2, y), "se": (x + w, y),
            "w": (x, y + h / 2), "e": (x + w, y + h / 2),
            "nw": (x, y + h), "n": (x + w / 2, y + h), "ne": (x + w, y + h),
        }
        for name in handles:
            ax_, ay_ = anchors[name]
            if abs(fx - ax_) <= HANDLE_TOLERANCE and abs(fy - ay_) <= HANDLE_TOLERANCE:
                return name
        return None

    def hit_test(self, fx: float, fy: float) -> Optional[Tuple[AxesModel, object]]:
        """Find the topmost object at figure-fraction point ``(fx, fy)``.

        Args:
            fx: Figure-fraction x coordinate.
            fy: Figure-fraction y coordinate.

        Returns:
            A ``(owning_axes, object)`` tuple, where ``object`` may be the
            axes itself, or ``None`` if the point hits empty canvas.
        """
        for axes_model in reversed(self.model.axes):
            hit = self._hit_test_axes_children(axes_model, fx, fy)
            if hit is not None:
                return (axes_model, hit)
            if _point_in_rect(fx, fy, axes_model.position) and not axes_model.locked:
                return (axes_model, axes_model)
        return None

    def _hit_test_axes_children(self, axes_model: AxesModel, fx: float, fy: float):
        for shape in reversed(axes_model.shapes):
            rect = axes_to_fig_rect(axes_model.position, (shape.x, shape.y, shape.width, shape.height))
            if _point_in_rect(fx, fy, rect):
                return shape
        for text in reversed(axes_model.texts):
            anchor = axes_to_fig_point(axes_model.position, (text.x, text.y))
            if _point_in_rect(fx, fy, _text_hit_rect(anchor, text.ha, text.va)):
                return text
        for annotation in reversed(axes_model.annotations):
            anchor = axes_to_fig_point(axes_model.position, (annotation.xtext, annotation.ytext))
            if _point_in_rect(fx, fy, _text_hit_rect(anchor, "center", "center")):
                return annotation
        return None

    def object_axes(self, obj: object) -> Optional[AxesModel]:
        """Return the :class:`AxesModel` that owns ``obj``, or ``None`` for a top-level axes."""
        if isinstance(obj, AxesModel):
            return None
        return self._parent_axes.get(id(obj))

    # ------------------------------------------------------------------ #
    # Move / resize (figure-fraction in, model coordinates out)
    # ------------------------------------------------------------------ #
    def get_object_position(self, obj: object) -> Optional[Tuple[float, float]]:
        """Get the figure-fraction position of an object's drag reference point.

        Returns ``None`` for an object that is no longer part of the scene
        (e.g. one that was just deleted but is still momentarily referenced,
        such as from a stale selection during a delete gesture).
        """
        if isinstance(obj, AxesModel):
            return (obj.position[0], obj.position[1])
        parent = self.object_axes(obj)
        if parent is None:
            return None
        if isinstance(obj, AnnotationModel):
            return axes_to_fig_point(parent.position, (obj.xtext, obj.ytext))
        return axes_to_fig_point(parent.position, (obj.x, obj.y))

    def set_object_position(self, obj: object, fig_pos: Tuple[float, float]) -> None:
        """Move an object so its drag reference point sits at ``fig_pos``."""
        if isinstance(obj, AxesModel):
            _l, _b, w, h = obj.position
            obj.position = (fig_pos[0], fig_pos[1], w, h)
            return
        parent = self.object_axes(obj)
        if parent is None:
            return
        new_ax_x, new_ax_y = fig_to_axes_point(parent.position, fig_pos)
        if isinstance(obj, AnnotationModel):
            dx, dy = new_ax_x - obj.xtext, new_ax_y - obj.ytext
            obj.xtext, obj.ytext = new_ax_x, new_ax_y
            obj.x, obj.y = obj.x + dx, obj.y + dy
            return
        dx, dy = new_ax_x - obj.x, new_ax_y - obj.y
        if isinstance(obj, ShapeModel) and obj.points:
            obj.points = [(px + dx, py + dy) for px, py in obj.points]
        obj.x, obj.y = new_ax_x, new_ax_y

    def get_object_rect(self, obj: object) -> Optional[Tuple[float, float, float, float]]:
        """Get the figure-fraction bounding rect of a resizable object."""
        if isinstance(obj, AxesModel):
            return tuple(obj.position)
        parent = self.object_axes(obj)
        if parent is None or not isinstance(obj, ShapeModel):
            return None
        return axes_to_fig_rect(parent.position, (obj.x, obj.y, obj.width, obj.height))

    def set_object_rect(self, obj: object, fig_rect: Tuple[float, float, float, float]) -> None:
        """Set the figure-fraction bounding rect of a resizable object."""
        if isinstance(obj, AxesModel):
            obj.position = tuple(fig_rect)
            return
        parent = self.object_axes(obj)
        if parent is None or not isinstance(obj, ShapeModel):
            return
        x0, y0 = fig_to_axes_point(parent.position, (fig_rect[0], fig_rect[1]))
        x1, y1 = fig_to_axes_point(parent.position, (fig_rect[0] + fig_rect[2], fig_rect[1] + fig_rect[3]))
        obj.x, obj.y, obj.width, obj.height = x0, y0, x1 - x0, y1 - y0

    def commit_move(self, obj: object, old_pos: Tuple[float, float], new_pos: Tuple[float, float]) -> None:
        """Push an undoable :class:`MoveObjectCommand` for an already-applied move."""
        command = MoveObjectCommand(obj.name, lambda p: self.set_object_position(obj, p), old_pos, new_pos, self.on_scene_changed)
        self.undo_manager.push_applied(command)

    def commit_resize(self, obj: object, old_rect, new_rect) -> None:
        """Push an undoable :class:`ResizeObjectCommand` for an already-applied resize."""
        command = ResizeObjectCommand(obj.name, lambda r: self.set_object_rect(obj, r), old_rect, new_rect, self.on_scene_changed)
        self.undo_manager.push_applied(command)

    def delete_selection(self) -> None:
        """Delete every currently selected object as one undoable macro step."""
        from ..commands.delete import DeleteObjectCommand

        commands = []
        for obj in list(self._selection):
            container = self._container_of(obj)
            if container is not None:
                commands.append(DeleteObjectCommand(container, obj, self.on_scene_changed))
        if not commands:
            return
        macro = MacroCommand(commands, label="Delete Selection")
        # Clear the selection before the delete executes (which triggers a
        # rebuild): the overlay-drawing code must never try to look up the
        # figure-fraction position of an object that is mid-deletion.
        self.set_selection([])
        self.undo_manager.push(macro)

    def add_clone(self, obj: object) -> Optional[object]:
        """Deep-copy ``obj`` with a fresh id/name and add it as an undoable command.

        Used by both the object tree's "Duplicate" action and the
        Edit > Paste action, so there is exactly one place that knows how
        to re-parent a cloned object of any scene-object type.

        Args:
            obj: The object to clone. Its owning axes (or the figure, for
                an :class:`~matplotlib_designer.models.axes_model.AxesModel`)
                is inferred automatically.

        Returns:
            The newly created clone, or ``None`` if ``obj``'s type is not
            clonable (e.g. it no longer belongs to this document).
        """
        import copy as _copy
        from dataclasses import replace as _replace

        from ..commands.add_axes import AddAxesCommand
        from ..commands.add_arrow import AddAnnotationCommand
        from ..commands.add_plot import AddPlotCommand
        from ..commands.add_shape import AddShapeCommand
        from ..commands.add_text import AddTextCommand
        from ..models.base_model import next_id

        clone = _replace(_copy.deepcopy(obj), id=next_id(), name=f"{obj.name} Copy")
        parent_axes = self.object_axes(obj)
        on_change = self.on_scene_changed
        if isinstance(obj, AxesModel):
            command = AddAxesCommand(self.model, clone, on_change)
        elif parent_axes is None:
            return None
        elif isinstance(obj, TextModel):
            command = AddTextCommand(parent_axes, clone, on_change)
        elif isinstance(obj, ShapeModel):
            command = AddShapeCommand(parent_axes, clone, on_change)
        elif isinstance(obj, AnnotationModel):
            command = AddAnnotationCommand(parent_axes, clone, on_change)
        elif isinstance(obj, PlotModel):
            command = AddPlotCommand(parent_axes, clone, on_change)
        else:
            return None
        self.undo_manager.push(command)
        return clone

    def _container_of(self, obj: object) -> Optional[list]:
        if isinstance(obj, AxesModel):
            return self.model.axes
        parent = self.object_axes(obj)
        if parent is None:
            return None
        if isinstance(obj, TextModel):
            return parent.texts
        if isinstance(obj, ShapeModel):
            return parent.shapes
        if isinstance(obj, AnnotationModel):
            return parent.annotations
        if isinstance(obj, PlotModel):
            return parent.plots
        return None

    # ------------------------------------------------------------------ #
    # Rubber-band selection & creation previews (overlay drawing)
    # ------------------------------------------------------------------ #
    def start_rubber_band(self, fx: float, fy: float) -> None:
        """Begin a rubber-band selection gesture at a figure-fraction point."""
        self._rubber_band_start = (fx, fy)

    def update_rubber_band(self, fx: float, fy: float) -> None:
        """Update the live rubber-band rectangle and redraw the overlay."""
        if self._rubber_band_start is None:
            return
        self._rubber_band_current = (fx, fy)
        self.draw_idle()

    def finish_rubber_band(self) -> None:
        """Select every object whose reference point lies within the band."""
        if self._rubber_band_start is None:
            return
        x0, y0 = self._rubber_band_start
        x1, y1 = getattr(self, "_rubber_band_current", (x0, y0))
        rect = (min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0))
        found = []
        for axes_model in self.model.axes:
            if _point_in_rect(*axes_model.position[:2], rect):
                found.append(axes_model)
            for obj in axes_model.all_children():
                if isinstance(obj, PlotModel):
                    continue
                pos = self.get_object_position(obj)
                if _point_in_rect(pos[0], pos[1], rect):
                    found.append(obj)
        self._rubber_band_start = None
        self.set_selection(found)

    def set_preview_shape(self, kind: str, axes_model: AxesModel, x0: float, y0: float, x1: float, y1: float) -> None:
        """Show a live preview rectangle/ellipse while a shape tool is dragging."""
        self._preview = ("shape", kind, axes_model, x0, y0, x1, y1)
        self.draw_idle()

    def set_preview_line(self, axes_model: AxesModel, x0: float, y0: float, x1: float, y1: float) -> None:
        """Show a live preview line while the line tool is dragging."""
        self._preview = ("line", None, axes_model, x0, y0, x1, y1)
        self.draw_idle()

    def set_preview_arrow(self, axes_model: AxesModel, x0: float, y0: float, x1: float, y1: float) -> None:
        """Show a live preview arrow while the arrow/annotation tool is dragging."""
        self._preview = ("arrow", None, axes_model, x0, y0, x1, y1)
        self.draw_idle()

    def clear_preview(self) -> None:
        """Clear any in-progress creation preview."""
        self._preview = None
        self.draw_idle()

    def request_inline_edit(self, obj: object) -> None:
        """Prompt for new text content and apply it as an undoable change.

        Args:
            obj: A :class:`TextModel` or :class:`AnnotationModel` instance.
        """
        attr = "content" if isinstance(obj, TextModel) else "text"
        current = getattr(obj, attr)
        new_value, ok = QInputDialog.getMultiLineText(self, "Edit Text", "Content:", current)
        if ok and new_value != current:
            self.undo_manager.push(PropertyChangeCommand(obj, attr, new_value, self.on_scene_changed))

    # ------------------------------------------------------------------ #
    # Overlay drawing
    # ------------------------------------------------------------------ #
    def _draw_selection_overlay(self) -> None:
        ax = getattr(self, "_overlay_ax", None)
        if ax is None:
            return
        for artist in list(ax.patches) + list(ax.lines):
            artist.remove()

        for obj in self._selection:
            rect = self.get_object_rect(obj)
            if rect is None:
                rect = self._point_rect_for(obj)
            if rect is None:
                continue
            x, y, w, h = rect
            ax.add_patch(Rectangle((x, y), w, h, fill=False, edgecolor="#2f8fff", linewidth=1.5, linestyle="--", zorder=100))
            for handle in self.get_selection_handles(obj):
                hx, hy = self._handle_point(rect, handle)
                ax.add_patch(Rectangle((hx - 0.006, hy - 0.006), 0.012, 0.012, facecolor="#2f8fff", edgecolor="white", zorder=101))

        if self._rubber_band_start is not None:
            x0, y0 = self._rubber_band_start
            x1, y1 = getattr(self, "_rubber_band_current", (x0, y0))
            rect = (min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0))
            ax.add_patch(Rectangle(rect[:2], rect[2], rect[3], fill=True, facecolor="#2f8fff", alpha=0.15,
                                    edgecolor="#2f8fff", linewidth=1, zorder=100))

        preview = getattr(self, "_preview", None)
        if preview is not None:
            self._draw_preview(ax, preview)

    def _draw_preview(self, ax, preview) -> None:
        kind, shape_kind, axes_model, x0, y0, x1, y1 = preview
        p0 = axes_to_fig_point(axes_model.position, (x0, y0))
        p1 = axes_to_fig_point(axes_model.position, (x1, y1))
        if kind == "shape":
            rx, ry = min(p0[0], p1[0]), min(p0[1], p1[1])
            rw, rh = abs(p1[0] - p0[0]), abs(p1[1] - p0[1])
            if shape_kind == "rectangle":
                ax.add_patch(Rectangle((rx, ry), rw, rh, fill=False, edgecolor="#2f8fff", linestyle="--", zorder=100))
            else:
                ax.add_patch(Ellipse((rx + rw / 2, ry + rh / 2), rw, rh, fill=False, edgecolor="#2f8fff", linestyle="--", zorder=100))
        else:
            ax.add_line(Line2D([p0[0], p1[0]], [p0[1], p1[1]], color="#2f8fff", linestyle="--", zorder=100))

    def _point_rect_for(self, obj) -> Optional[Tuple[float, float, float, float]]:
        if isinstance(obj, PlotModel):
            return None
        pos = self.get_object_position(obj)
        if pos is None:
            return None
        ha = getattr(obj, "ha", "center")
        va = getattr(obj, "va", "center")
        return _text_hit_rect(pos, ha, va)

    @staticmethod
    def _handle_point(rect: Tuple[float, float, float, float], handle: str) -> Tuple[float, float]:
        x, y, w, h = rect
        table = {
            "sw": (x, y), "s": (x + w / 2, y), "se": (x + w, y),
            "w": (x, y + h / 2), "e": (x + w, y + h / 2),
            "nw": (x, y + h), "n": (x + w / 2, y + h), "ne": (x + w, y + h),
        }
        return table[handle]

    # ------------------------------------------------------------------ #
    # Qt / Matplotlib event plumbing
    # ------------------------------------------------------------------ #
    def _make_context(self, event) -> Optional[ToolContext]:
        if event.x is None or event.y is None:
            return None
        fx = event.x / self.figure.bbox.width
        fy = event.y / self.figure.bbox.height
        axes_model, ax_x, ax_y = None, None, None
        for candidate in reversed(self.model.axes):
            if _point_in_rect(fx, fy, candidate.position):
                axes_model = candidate
                ax_x, ax_y = fig_to_axes_point(candidate.position, (fx, fy))
                break
        from PySide6.QtWidgets import QApplication
        mods = QApplication.keyboardModifiers()
        return ToolContext(
            canvas=self, axes_model=axes_model, ax_x=ax_x, ax_y=ax_y, fig_x=fx, fig_y=fy,
            shift=bool(mods & Qt.ShiftModifier), ctrl=bool(mods & Qt.ControlModifier), mpl_event=event,
        )

    def _on_press(self, event) -> None:
        ctx = self._make_context(event)
        if ctx is None or event.button != 1:
            return
        self._dragging = True
        self._tools[self._active_tool_name].on_press(ctx)

    def _on_move(self, event) -> None:
        if not self._dragging:
            return
        ctx = self._make_context(event)
        if ctx is None:
            return
        self._tools[self._active_tool_name].on_move(ctx)

    def _on_release(self, event) -> None:
        if not self._dragging:
            return
        self._dragging = False
        ctx = self._make_context(event)
        if ctx is None:
            ctx = ToolContext(canvas=self, axes_model=None, ax_x=None, ax_y=None, fig_x=0, fig_y=0)
        self._tools[self._active_tool_name].on_release(ctx)

    def _on_scroll(self, event) -> None:
        """Zoom the data view of the axes under the cursor with the scroll wheel."""
        if event.inaxes is None or event.inaxes is getattr(self, "_overlay_ax", None):
            return
        ax = event.inaxes
        scale = 0.9 if event.button == "up" else 1.1
        xlim, ylim = ax.get_xlim(), ax.get_ylim()
        xdata, ydata = event.xdata, event.ydata
        if xdata is None or ydata is None:
            return
        ax.set_xlim([xdata + (v - xdata) * scale for v in xlim])
        ax.set_ylim([ydata + (v - ydata) * scale for v in ylim])
        self.mpl_canvas.draw_idle()
