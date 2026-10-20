import asyncio
from pathlib import Path
from PIL import Image

THUMBNAIL_DIR = Path("thumbnails")
THUMBNAIL_SIZE = (256, 256)


async def generate(photo_id: int, source_path: str) -> str:
    """Generate a 256x256 center-crop JPEG thumbnail. Returns the thumbnail path string."""
    thumb_path = THUMBNAIL_DIR / f"{photo_id}.jpg"
    if thumb_path.exists():
        return str(thumb_path)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _generate_sync, source_path, thumb_path)
    return str(thumb_path)


def _generate_sync(source_path: str, thumb_path: Path) -> None:
    thumb_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source_path) as img:
        img = img.convert("RGB")
        w, h = img.size
        min_dim = min(w, h)
        left = (w - min_dim) // 2
        top = (h - min_dim) // 2
        img = img.crop((left, top, left + min_dim, top + min_dim))
        img = img.resize(THUMBNAIL_SIZE, Image.LANCZOS)
        img.save(str(thumb_path), "JPEG", quality=85)


async def repair_missing(photos: list) -> None:
    """Re-generate thumbnails for photos whose cached thumbnail is absent."""
    for photo in photos:
        if not photo.thumbnail_path or not Path(photo.thumbnail_path).exists():
            try:
                source = Path("photos") / photo.file_path
                if source.exists():
                    new_path = await generate(photo.id, str(source))
                    # Update DB reference
                    from src.services import db
                    conn = db.get_connection()
                    await conn.execute(
                        "UPDATE photos SET thumbnail_path = ? WHERE id = ?",
                        (new_path, photo.id),
                    )
                    await conn.commit()
            except Exception:
                pass
