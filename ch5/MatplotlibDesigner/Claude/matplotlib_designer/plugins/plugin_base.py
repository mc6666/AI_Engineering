"""Base class every plugin must implement."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class PluginBase(ABC):
    """Contract for a Matplotlib Designer plugin.

    A plugin can contribute a new plot type, a toolbar action, a menu
    action, and/or a dock widget by implementing :meth:`register` and
    using the ``window`` object's public APIs (``window.add_menu_action``,
    ``window.add_dock_widget``, ``window.canvas``, ...).

    Attributes:
        name: Human readable plugin name shown in the Plugin Manager.
        version: Plugin version string.
    """

    name: str = "Unnamed Plugin"
    version: str = "0.1.0"

    @abstractmethod
    def register(self, window: Any) -> None:
        """Register the plugin's contributions against the main window.

        Args:
            window: The running
                :class:`~matplotlib_designer.designer.main_window.MainWindow`.
        """
        raise NotImplementedError
