"""Example plugin demonstrating the Matplotlib Designer plugin API.

Drop additional ``*.py`` files defining a ``Plugin`` class in this
directory to extend the application; each one is discovered and
registered automatically at startup by
:func:`matplotlib_designer.plugins.loader.load_plugins`.
"""
from __future__ import annotations

from PySide6.QtWidgets import QMessageBox

from matplotlib_designer.plugins.plugin_base import PluginBase


class Plugin(PluginBase):
    """Adds a "Say Hello" action to the Help menu as a minimal example."""

    name = "Example Plugin"
    version = "1.0.0"

    def register(self, window) -> None:
        """Contribute a single menu action.

        Args:
            window: The running main window.
        """
        window.add_menu_action("Help", "Say Hello (Example Plugin)", self._say_hello)

    def _say_hello(self) -> None:
        QMessageBox.information(None, "Example Plugin", "Hello from a Matplotlib Designer plugin!")
