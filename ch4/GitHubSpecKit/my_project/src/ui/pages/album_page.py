from nicegui import ui
from src.services import album_service, photo_service
from src.ui.components.photo_tile import photo_tile
from src.ui.components.lightbox import lightbox


@ui.page("/album/{album_id}")
async def album_page(album_id: int) -> None:
    album = await album_service.get_album_by_id(album_id)
    if album is None:
        ui.notify("Album not found.", type="warning")
        ui.navigate.to("/")
        return

    photos = await photo_service.get_photos_by_album(album_id)

    with ui.row().classes("items-center mb-4 gap-4"):
        ui.button("← Albums", on_click=lambda: ui.navigate.to("/")).props("flat")
        label_input = ui.input(value=album.label).classes("text-2xl font-bold flex-1")

        async def on_label_blur() -> None:
            new_label = label_input.value.strip()
            if new_label and new_label != album.label:
                updated = await album_service.update_label(album_id, new_label)
                if updated:
                    album.label = updated.label
                    ui.notify("Album renamed.", type="positive")

        label_input.on("blur", on_label_blur)

    if album.date != album.label:
        ui.label(album.date).classes("text-gray-500 text-sm mb-4")

    if not photos:
        ui.label("This album is empty.").classes("text-gray-500 text-xl")
        return

    def open_lightbox(photo_id: int) -> None:
        photo = next((p for p in photos if p.id == photo_id), None)
        if photo:
            lightbox(f"/photos/{photo.file_path}", photo.filename)

    with ui.element("div").classes("flex flex-wrap gap-4"):
        for p in photos:
            photo_tile(
                photo_id=p.id,
                thumbnail_url=f"/thumbnails/{p.id}.jpg",
                alt_text=p.filename,
                on_click=open_lightbox,
            )
