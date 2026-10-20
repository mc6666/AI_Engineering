"""Command-pattern actions for Matplotlib Designer.

Every mutation to the design document is expressed as a
:class:`~matplotlib_designer.commands.command.Command` and executed through
the :class:`~matplotlib_designer.commands.undo.UndoManager`, giving the
application unlimited, uniform undo/redo.
"""

from .command import Command
from .undo import UndoManager
from .redo import MacroCommand
from .add_text import AddTextCommand
from .add_arrow import AddAnnotationCommand
from .add_shape import AddShapeCommand
from .add_plot import AddPlotCommand
from .add_axes import AddAxesCommand
from .delete import DeleteObjectCommand
from .move import MoveObjectCommand
from .resize import ResizeObjectCommand
from .property_change import PropertyChangeCommand

__all__ = [
    "Command",
    "UndoManager",
    "MacroCommand",
    "AddTextCommand",
    "AddAnnotationCommand",
    "AddShapeCommand",
    "AddPlotCommand",
    "AddAxesCommand",
    "DeleteObjectCommand",
    "MoveObjectCommand",
    "ResizeObjectCommand",
    "PropertyChangeCommand",
]
