"""Save and load ``.mdz`` (Matplotlib Designer) JSON project files.

The project format is a plain JSON document produced by
:meth:`~matplotlib_designer.models.figure_model.FigureModel.to_dict`. It
captures the figure, every axes, and all plots/shapes/annotations/text and
their properties, so a saved project reopens pixel-for-pixel identical to
how it was left, including layer order and lock/visibility state.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from ..models.figure_model import FigureModel

#: Bumped whenever the on-disk schema changes in a way that needs migration.
PROJECT_FORMAT_VERSION = 1


def save_project(figure: FigureModel, path: Union[str, Path]) -> None:
    """Serialize ``figure`` to a JSON project file.

    Args:
        figure: The document to save.
        path: Destination file path. Parent directories are not created
            automatically.
    """
    payload = {
        "format": "matplotlib-designer-project",
        "format_version": PROJECT_FORMAT_VERSION,
        "figure": figure.to_dict(),
    }
    Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_project(path: Union[str, Path]) -> FigureModel:
    """Load a JSON project file previously written by :func:`save_project`.

    Args:
        path: Path to the project file.

    Returns:
        The reconstructed :class:`~matplotlib_designer.models.figure_model.FigureModel`.

    Raises:
        ValueError: If the file is not a recognized project file.
    """
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("format") != "matplotlib-designer-project":
        raise ValueError(f"Not a Matplotlib Designer project file: {path}")
    return FigureModel.from_dict(payload["figure"])
