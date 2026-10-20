from typing import Callable
from nicegui import ui


def photo_tile(
    photo_id: int,
    thumbnail_url: str,
    alt_text: str,
    on_click: Callable[[int], None],
) -> None:
    """Reusable 256x256 photo tile component."""
    with ui.card().classes(
        "cursor-pointer p-0 overflow-hidden w-64 h-64"
    ).on("click", lambda pid=photo_id: on_click(pid)):
        ui.image(thumbnail_url).classes("w-full h-full object-cover").props(
            f'alt="{alt_text}"'
        )
