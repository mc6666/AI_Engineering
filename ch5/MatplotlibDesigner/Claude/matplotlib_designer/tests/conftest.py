"""Shared pytest fixtures: a headless Qt application for widget tests."""
from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import matplotlib

matplotlib.use("Agg")

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """A single, session-scoped ``QApplication`` for all widget-based tests."""
    app = QApplication.instance() or QApplication([])
    yield app
