"""Application bootstrap: Qt/Matplotlib backend setup and window launch."""
from __future__ import annotations

import sys

import matplotlib

matplotlib.use("QtAgg")

from PySide6.QtWidgets import QApplication  # noqa: E402  (backend must be set first)

from .designer.main_window import MainWindow  # noqa: E402


def run(argv: list[str] | None = None) -> int:
    """Create the ``QApplication``, show the main window, and run the event loop.

    Args:
        argv: Command-line arguments to pass to ``QApplication``; defaults
            to ``sys.argv``.

    Returns:
        The process exit code returned by the Qt event loop.
    """
    app = QApplication.instance() or QApplication(argv if argv is not None else sys.argv)
    app.setApplicationName("Matplotlib Designer")
    app.setOrganizationName("MatplotlibDesigner")
    window = MainWindow()
    window.show()
    return app.exec()
