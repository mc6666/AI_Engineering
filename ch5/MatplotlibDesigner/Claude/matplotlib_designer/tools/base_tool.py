"""Base interface and shared context object for interactive canvas tools."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from ..models.axes_model import AxesModel


@dataclass
class ToolContext:
    """Snapshot of a mouse event, handed to the active tool by the canvas.

    Attributes:
        canvas: The owning ``SceneCanvas`` (typed as ``Any`` to avoid a
            circular import between :mod:`tools` and :mod:`designer.canvas`).
        axes_model: The :class:`AxesModel` under the cursor, or ``None`` if
            the cursor is outside every axes.
        ax_x: Cursor x position in axes-fraction coordinates of
            ``axes_model`` (``None`` if ``axes_model`` is ``None``).
        ax_y: Cursor y position in axes-fraction coordinates of
            ``axes_model`` (``None`` if ``axes_model`` is ``None``).
        fig_x: Cursor x position in figure-fraction coordinates.
        fig_y: Cursor y position in figure-fraction coordinates.
        shift: Whether the Shift key is currently held.
        ctrl: Whether the Ctrl key is currently held.
        mpl_event: The raw Matplotlib mouse event, for tools (zoom/pan) that
            need real data-space coordinates (``inaxes``, ``xdata``, ``ydata``)
            rather than the model's axes-fraction coordinates.
    """

    canvas: Any
    axes_model: Optional[AxesModel]
    ax_x: Optional[float]
    ax_y: Optional[float]
    fig_x: float
    fig_y: float
    shift: bool = False
    ctrl: bool = False
    mpl_event: Any = None


class BaseTool:
    """Base class for every canvas tool.

    Subclasses override the handlers they care about; the default
    implementations do nothing. Tools are stateless between gestures except
    for whatever instance attributes they set in :meth:`on_press` and clear
    in :meth:`on_release`.

    Attributes:
        name: Identifier shown in the status bar and used by the toolbar.
    """

    name: str = "tool"

    def on_press(self, ctx: ToolContext) -> None:
        """Handle a mouse-button-press event.

        Args:
            ctx: The event context.
        """

    def on_move(self, ctx: ToolContext) -> None:
        """Handle a mouse-move event (called continuously while dragging).

        Args:
            ctx: The event context.
        """

    def on_release(self, ctx: ToolContext) -> None:
        """Handle a mouse-button-release event.

        Args:
            ctx: The event context.
        """

    def deactivate(self, canvas: Any) -> None:
        """Clean up any in-progress gesture state and previews.

        Called when the user switches to a different tool mid-gesture.

        Args:
            canvas: The owning ``SceneCanvas``.
        """
        canvas.clear_preview()
