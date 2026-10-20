import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nicegui import ui, app
from pydantic import BaseModel
from fastapi.responses import Response

from src.services import db, thumbnail_service
import src.ui.pages.main_page  # noqa: F401 — registers @ui.page("/")
import src.ui.pages.album_page  # noqa: F401 — registers @ui.page("/album/{album_id}")


class ReorderRequest(BaseModel):
    ordered_ids: list[int]


@app.get("/sw.js")
async def service_worker():
    return Response(
        content="self.addEventListener('install',()=>self.skipWaiting());self.addEventListener('activate',()=>self.registration.unregister());",
        media_type="application/javascript",
    )


@app.post("/api/albums/reorder")
async def reorder_albums(request: ReorderRequest):
    from src.services import album_service
    await album_service.update_display_order(request.ordered_ids)
    return {"status": "ok"}


async def _startup() -> None:
    await db.init("data/photo_organizer.db")
    app.add_media_files("/photos", "photos")
    app.add_media_files("/thumbnails", "thumbnails")
    # Repair thumbnails missing from cache on startup
    from src.services import photo_service
    all_photos = await photo_service.get_all_photos()
    await thumbnail_service.repair_missing(all_photos)


app.on_startup(_startup)
app.on_shutdown(db.close)

# if __name__ == "__main__":
ui.run(title="Photo Albums", port=8080)
