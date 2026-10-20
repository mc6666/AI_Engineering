from nicegui import ui


def album_card(album_id: int, label: str, cover_thumbnail_url: str | None) -> None:
    """Reusable album card component for the main page grid."""
    with ui.card().classes(
        "cursor-pointer hover:shadow-lg transition-shadow w-64 p-0 overflow-hidden"
    ).props(f'data-album-id="{album_id}"').on(
        "click", lambda: ui.navigate.to(f"/album/{album_id}")
    ):
        if cover_thumbnail_url:
            ui.image(cover_thumbnail_url).classes("w-full h-64 object-cover")
        else:
            with ui.element("div").classes(
                "w-full h-64 bg-gray-200 flex items-center justify-center"
            ):
                ui.icon("photo_library", size="4rem").classes("text-gray-400")
        ui.label(label).classes("text-center font-medium p-2 truncate w-full")
