import datetime
import hashlib
from pathlib import Path
from PIL import Image
from loguru import logger
import uuid
from src.models.photo import Photo
from src.services import db, album_service, thumbnail_service

PHOTOS_DIR = Path("photos")
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
_EXIF_DATE_ORIGINAL = 36867   # DateTimeOriginal
_EXIF_DATE_FALLBACK = 306     # DateTime


async def import_photo(filename: str, file_bytes: bytes) -> Photo:
    """Validate, store, extract EXIF date, assign album, generate thumbnail."""
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        raise ValueError(
            f"'{filename}' is not a supported image format. "
            "Supported formats: JPEG, PNG, GIF, WEBP."
        )

    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = _collision_safe_name(filename, file_bytes)
    dest_path = PHOTOS_DIR / safe_name

    # Duplicate detection: reject if this exact file content was already imported
    conn = db.get_connection()
    async with conn.execute(
        "SELECT id FROM photos WHERE file_path = ?", (safe_name,)
    ) as cursor:
        existing = await cursor.fetchone()
    if existing:
        raise ValueError(f"'{filename}' was already imported.")

    dest_path.write_bytes(file_bytes)

    date_taken, used_fallback = _extract_date(dest_path)
    album = await album_service.get_or_create_by_date(date_taken)

    import_date = datetime.datetime.now().isoformat(sep="T", timespec="seconds")
    conn = db.get_connection()
    async with conn.execute(
        "INSERT INTO photos (filename, file_path, date_taken, import_date, file_size, album_id) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            filename,
            safe_name,
            None if used_fallback else date_taken,
            import_date,
            len(file_bytes),
            album.id,
        ),
    ) as cursor:
        photo_id = cursor.lastrowid
    await conn.commit()

    thumb_path = await thumbnail_service.generate(photo_id, str(dest_path))
    await conn.execute(
        "UPDATE photos SET thumbnail_path = ? WHERE id = ?", (thumb_path, photo_id)
    )
    await conn.commit()

    await album_service.update_cover_photo(album.id, photo_id)

    return Photo(
        id=photo_id,
        filename=filename,
        file_path=safe_name,
        date_taken=None if used_fallback else date_taken,
        import_date=import_date,
        file_size=len(file_bytes),
        album_id=album.id,
        thumbnail_path=thumb_path,
    )


async def get_photos_by_album(album_id: int) -> list[Photo]:
    conn = db.get_connection()
    async with conn.execute(
        "SELECT * FROM photos WHERE album_id = ? ORDER BY date_taken ASC, import_date ASC",
        (album_id,),
    ) as cursor:
        rows = await cursor.fetchall()
    return [
        Photo(
            id=row["id"],
            filename=row["filename"],
            file_path=row["file_path"],
            date_taken=row["date_taken"],
            import_date=row["import_date"],
            file_size=row["file_size"],
            album_id=row["album_id"],
            thumbnail_path=row["thumbnail_path"],
        )
        for row in rows
    ]


async def get_all_photos() -> list[Photo]:
    conn = db.get_connection()
    async with conn.execute("SELECT * FROM photos") as cursor:
        rows = await cursor.fetchall()
    return [
        Photo(
            id=row["id"],
            filename=row["filename"],
            file_path=row["file_path"],
            date_taken=row["date_taken"],
            import_date=row["import_date"],
            file_size=row["file_size"],
            album_id=row["album_id"],
            thumbnail_path=row["thumbnail_path"],
        )
        for row in rows
    ]


def _collision_safe_name(original: str, data: bytes) -> str:
    # h = hashlib.sha1(data).hexdigest()[:8]
    unique_id = uuid.uuid4()
    stem = Path(original).stem[:40]
    suffix = Path(original).suffix.lower()
    return f"{unique_id}_{stem}{suffix}"


def _extract_date(path: Path) -> tuple[str, bool]:
    """Return (ISO date string, used_fallback). used_fallback=True when EXIF is absent."""
    try:
        with Image.open(path) as img:
            exif = img._getexif()  # type: ignore[attr-defined]
            if exif:
                for tag in (_EXIF_DATE_ORIGINAL, _EXIF_DATE_FALLBACK):
                    val = exif.get(tag)
                    if val:
                        date_part = str(val).split(" ")[0].replace(":", "-")
                        return date_part, False
    except Exception:
        pass
    return datetime.date.today().isoformat(), True
