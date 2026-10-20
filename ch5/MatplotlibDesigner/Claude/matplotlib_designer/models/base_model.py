"""Base classes shared by all scene object models in Matplotlib Designer.

This module defines :class:`SceneObject`, the common dataclass mixin that
every visual model (text, shape, annotation, plot, axes, figure) inherits
from. It centralizes identity, naming, z-ordering, visibility and locking
so the object tree and property panel can treat all objects uniformly.
"""
from __future__ import annotations

import itertools
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict

_counter = itertools.count(1)


def next_id() -> str:
    """Return a short, unique id for a new scene object.

    Returns:
        A unique identifier combining a monotonic counter and a random
        suffix so ids remain stable, sortable and human readable.
    """
    return f"obj{next(_counter)}_{uuid.uuid4().hex[:6]}"


@dataclass
class SceneObject:
    """Common attributes shared by every object that can appear in the scene.

    Attributes:
        id: Unique, stable identifier for the object.
        name: Human readable, user-editable label shown in the object tree.
        visible: Whether the object is rendered on the canvas.
        locked: Whether the object can be selected/moved/edited on canvas.
        z_order: Paint/selection order; higher values draw on top.
        opacity: Alpha blending value in the range ``[0, 1]``.
    """

    id: str = field(default_factory=next_id)
    name: str = "Object"
    visible: bool = True
    locked: bool = False
    z_order: int = 0
    opacity: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize base attributes to a plain ``dict``.

        Subclasses should call ``super().to_dict()`` and update the result
        with their own fields.

        Returns:
            A JSON-serializable dictionary of the base attributes.
        """
        return {
            "id": self.id,
            "name": self.name,
            "visible": self.visible,
            "locked": self.locked,
            "z_order": self.z_order,
            "opacity": self.opacity,
        }

    def apply_base(self, data: Dict[str, Any]) -> None:
        """Apply base attribute values from a serialized ``dict`` in place.

        Args:
            data: A dictionary previously produced by :meth:`to_dict`.
        """
        self.id = data.get("id", self.id)
        self.name = data.get("name", self.name)
        self.visible = data.get("visible", self.visible)
        self.locked = data.get("locked", self.locked)
        self.z_order = data.get("z_order", self.z_order)
        self.opacity = data.get("opacity", self.opacity)
