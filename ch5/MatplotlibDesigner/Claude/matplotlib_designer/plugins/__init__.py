"""Plugin system: third-party extensions register plots, actions and docks.

Plugins are plain Python modules placed under this package (or any
directory added to ``sys.path``) that define a subclass of
:class:`~matplotlib_designer.plugins.plugin_base.PluginBase` named
``Plugin``. :func:`~matplotlib_designer.plugins.loader.load_plugins`
discovers and registers them against the running
:class:`~matplotlib_designer.designer.main_window.MainWindow`.
"""

from .plugin_base import PluginBase
from .loader import load_plugins

__all__ = ["PluginBase", "load_plugins"]
