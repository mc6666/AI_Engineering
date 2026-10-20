from pathlib import Path

from nicegui import ui
from src.services import album_service, photo_service
from src.ui.components.album_card import album_card
from loguru import logger

_SORTABLE_CDN = (
    '<script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.2/Sortable.min.js"></script>'
)
_SORTABLE_INIT_JS = """
(function() {
    const container = document.getElementById('album-grid');
    if (container && !container._sortable) {
        container._sortable = new Sortable(container, {
            animation: 150,
            onEnd: function() {
                const cards = container.querySelectorAll('[data-album-id]');
                const ids = Array.from(cards).map(c => parseInt(c.dataset.albumId));
                fetch('/api/albums/reorder', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ordered_ids: ids})
                });
            }
        });
    }
})();
"""


@ui.page("/")
async def main_page() -> None:
    ui.add_head_html(_SORTABLE_CDN)
    ui.label("Photo Albums").classes("text-3xl font-bold mb-4")

    async def handle_import(e) -> None:
        for upload_event_arg in e.files if hasattr(e, "files") else [e]:
            try:
                content = await upload_event_arg.file.read()
                name = upload_event_arg.file.name 
                # logger.debug(f'content:{content}')
                await photo_service.import_photo(name, content)
            except ValueError as exc:
                ui.notify(str(exc), type="negative")
        ui.notify("Import complete", type="positive")
        await _refresh_grid(grid_container)

    def handle_reject(e) -> None:
        logger.debug(f'e:{e}')
        name = e.name if hasattr(e, "name") else "file"
        ui.notify(
            f"'{name}' is not a supported image format. "
            "Supported formats: JPEG, PNG, GIF, WEBP.",
            type="negative",
        )

    ui.upload(
        label="Import Photos",
        multiple=True,
        on_upload=handle_import,
        on_rejected=handle_reject,
        auto_upload=True,
    ).classes("mb-6")

    grid_container = ui.element("div").props('id="album-grid"').classes("flex flex-wrap gap-4")
    await _refresh_grid(grid_container)


async def _refresh_grid(grid_container) -> None:
    grid_container.clear()
    albums = await album_service.get_all_albums()
    with grid_container:
        if not albums:
            ui.label("No albums yet. Import some photos to get started.").classes(
                "text-gray-500 text-xl"
            )
        else:
            for alb in albums:
                thumb_url = (
                    f"/thumbnails/{alb.cover_photo_id}.jpg" if alb.cover_photo_id else None
                )
                album_card(alb.id, alb.label, thumb_url)
    if albums:
        await ui.run_javascript(_SORTABLE_INIT_JS)
