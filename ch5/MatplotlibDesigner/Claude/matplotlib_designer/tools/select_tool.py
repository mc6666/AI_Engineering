"""The default Selection tool: click, multi-select, drag-move, resize."""
from __future__ import annotations

from typing import Optional, Tuple

from .base_tool import BaseTool, ToolContext

#: Minimum size (figure-fraction units) an object may be resized down to.
MIN_SIZE = 0.01


class SelectTool(BaseTool):
    """Selects, moves and resizes objects on the canvas.

    Behavior:
        * Click an object: select it (replacing the current selection).
        * Shift/Ctrl+Click: toggle the object into/out of the selection.
        * Click and drag an object: move the whole selection.
        * Drag a resize handle of a single selected object: resize it.
        * Click and drag empty space: rubber-band select everything the
          band overlaps.
    """

    name = "select"

    def __init__(self) -> None:
        """Initialize with no gesture in progress."""
        self._mode: Optional[str] = None  # "move" | "resize" | "band"
        self._handle: Optional[str] = None
        self._start_fig: Tuple[float, float] = (0.0, 0.0)
        self._object_starts: dict = {}

    def on_press(self, ctx: ToolContext) -> None:
        """Begin a move, resize or rubber-band gesture."""
        canvas = ctx.canvas
        self._start_fig = (ctx.fig_x, ctx.fig_y)

        handle = canvas.hit_test_handle(ctx.fig_x, ctx.fig_y)
        if handle is not None:
            self._mode = "resize"
            self._handle = handle
            obj = canvas.selection[0]
            self._object_starts = {id(obj): (obj, canvas.get_object_rect(obj))}
            return

        hit = canvas.hit_test(ctx.fig_x, ctx.fig_y)
        if hit is None:
            if not (ctx.shift or ctx.ctrl):
                canvas.set_selection([])
            self._mode = "band"
            canvas.start_rubber_band(ctx.fig_x, ctx.fig_y)
            return

        _axes, obj = hit
        if getattr(obj, "locked", False):
            self._mode = None
            return

        if ctx.shift or ctx.ctrl:
            canvas.toggle_selection(obj)
        elif obj not in canvas.selection:
            canvas.set_selection([obj])

        if obj in canvas.selection:
            self._mode = "move"
            self._object_starts = {
                id(o): (o, canvas.get_object_position(o)) for o in canvas.selection
            }
        else:
            self._mode = None

    def on_move(self, ctx: ToolContext) -> None:
        """Continue the in-progress move, resize or rubber-band gesture."""
        canvas = ctx.canvas
        if self._mode == "band":
            canvas.update_rubber_band(ctx.fig_x, ctx.fig_y)
        elif self._mode == "move":
            dx = ctx.fig_x - self._start_fig[0]
            dy = ctx.fig_y - self._start_fig[1]
            for _key, (obj, (x0, y0)) in self._object_starts.items():
                canvas.set_object_position(obj, (x0 + dx, y0 + dy))
            canvas.draw_idle()
        elif self._mode == "resize":
            dx = ctx.fig_x - self._start_fig[0]
            dy = ctx.fig_y - self._start_fig[1]
            (obj, rect0) = next(iter(self._object_starts.values()))
            new_rect = _apply_handle_delta(rect0, self._handle, dx, dy)
            canvas.set_object_rect(obj, new_rect)
            canvas.draw_idle()

    def on_release(self, ctx: ToolContext) -> None:
        """Finish the gesture, committing an undoable command."""
        canvas = ctx.canvas
        if self._mode == "band":
            canvas.finish_rubber_band()
        elif self._mode == "move":
            for _key, (obj, old_pos) in self._object_starts.items():
                new_pos = canvas.get_object_position(obj)
                if new_pos != old_pos:
                    canvas.commit_move(obj, old_pos, new_pos)
        elif self._mode == "resize":
            (obj, rect0) = next(iter(self._object_starts.values()))
            new_rect = canvas.get_object_rect(obj)
            if new_rect != rect0:
                canvas.commit_resize(obj, rect0, new_rect)
        self._mode = None
        self._handle = None
        self._object_starts = {}
        canvas.clear_preview()
        canvas.draw_idle()


def _apply_handle_delta(
    rect: Tuple[float, float, float, float], handle: str, dx: float, dy: float
) -> Tuple[float, float, float, float]:
    """Compute a new ``(x, y, w, h)`` rect after dragging one of its handles.

    Args:
        rect: Original ``(x, y, w, h)`` rectangle.
        handle: Which handle is being dragged: a combination of
            ``"n"``/``"s"`` and ``"e"``/``"w"`` (e.g. ``"se"``), or a single
            edge letter.
        dx: Horizontal mouse movement since the drag started.
        dy: Vertical mouse movement since the drag started.

    Returns:
        The updated rectangle, clamped so width/height never go below
        :data:`MIN_SIZE`.
    """
    x, y, w, h = rect
    if "w" in handle:
        new_x = x + dx
        new_w = w - dx
        if new_w < MIN_SIZE:
            new_x = x + w - MIN_SIZE
            new_w = MIN_SIZE
        x, w = new_x, new_w
    if "e" in handle:
        w = max(MIN_SIZE, w + dx)
    if "s" in handle:
        new_y = y + dy
        new_h = h - dy
        if new_h < MIN_SIZE:
            new_y = y + h - MIN_SIZE
            new_h = MIN_SIZE
        y, h = new_y, new_h
    if "n" in handle:
        h = max(MIN_SIZE, h + dy)
    return (x, y, w, h)
