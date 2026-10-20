"""Discovers and registers plugins from a directory at application start."""
from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path
from typing import Any, List

from .plugin_base import PluginBase


def load_plugins(directory: Path, window: Any) -> List[PluginBase]:
    """Import every ``*.py`` module in ``directory`` and register its plugin.

    A module is treated as a plugin if it defines a top-level class named
    ``Plugin`` that subclasses :class:`PluginBase`. Import or registration
    errors in one plugin are logged and skipped rather than crashing the
    application, so a single broken plugin cannot block startup.

    Args:
        directory: Folder to scan for plugin modules.
        window: The running main window, passed to each plugin's
            :meth:`~PluginBase.register`.

    Returns:
        The list of successfully loaded plugin instances.
    """
    loaded: List[PluginBase] = []
    if not directory.is_dir():
        return loaded

    for path in sorted(directory.glob("*.py")):
        if path.name.startswith("_"):
            continue
        try:
            spec = importlib.util.spec_from_file_location(f"mdz_plugin_{path.stem}", path)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            plugin_cls = getattr(module, "Plugin", None)
            if plugin_cls is None or not inspect.isclass(plugin_cls) or not issubclass(plugin_cls, PluginBase):
                continue
            plugin = plugin_cls()
            plugin.register(window)
            loaded.append(plugin)
        except Exception as exc:  # noqa: BLE001 - a bad plugin must never crash the app
            print(f"[plugins] Failed to load {path.name}: {exc}")
    return loaded
