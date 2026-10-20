import io
import os
import tempfile
import pytest
from PIL import Image
from src.services import db, photo_service


@pytest.fixture(autouse=True)
async def isolated_db(tmp_path, monkeypatch):
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    await db.init(db_path)
    # Redirect storage to temp dirs
    monkeypatch.setattr(photo_service, "PHOTOS_DIR", tmp_path / "photos")
    import src.services.thumbnail_service as ts
    monkeypatch.setattr(ts, "THUMBNAIL_DIR", tmp_path / "thumbnails")
    yield
    await db.close()
    os.unlink(db_path)


def _make_jpeg_bytes(date_str: str | None = None) -> bytes:
    """Create a minimal JPEG in memory, optionally with EXIF DateTimeOriginal."""
    img = Image.new("RGB", (100, 100), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, "JPEG")
    return buf.getvalue()


def _make_png_bytes() -> bytes:
    img = Image.new("RGB", (50, 50), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


# --- import_photo ---

async def test_import_photo_creates_album_and_photo():
    photo = await photo_service.import_photo("test.jpg", _make_jpeg_bytes())
    assert photo.id is not None
    assert photo.album_id is not None
    assert photo.filename == "test.jpg"


async def test_import_photo_rejects_non_image():
    with pytest.raises(ValueError, match="not a supported image format"):
        await photo_service.import_photo("document.pdf", b"%PDF-1.4 fake content")


async def test_import_photo_rejects_txt():
    with pytest.raises(ValueError, match="not a supported image format"):
        await photo_service.import_photo("notes.txt", b"some text")


async def test_import_photo_same_date_goes_to_same_album():
    p1 = await photo_service.import_photo("a.jpg", _make_jpeg_bytes())
    p2 = await photo_service.import_photo("b.png", _make_png_bytes())
    # Both lack EXIF so both fall back to today; same album
    assert p1.album_id == p2.album_id


async def test_import_photo_generates_thumbnail(tmp_path):
    photo = await photo_service.import_photo("test.jpg", _make_jpeg_bytes())
    assert photo.thumbnail_path is not None


# --- get_photos_by_album ---

async def test_get_photos_by_album_empty():
    from src.services import album_service
    album = await album_service.get_or_create_by_date("2024-06-15")
    photos = await photo_service.get_photos_by_album(album.id)
    assert photos == []


async def test_get_photos_by_album_returns_correct_photos():
    p1 = await photo_service.import_photo("a.jpg", _make_jpeg_bytes())
    p2 = await photo_service.import_photo("b.png", _make_png_bytes())
    photos = await photo_service.get_photos_by_album(p1.album_id)
    photo_ids = {p.id for p in photos}
    assert p1.id in photo_ids
    assert p2.id in photo_ids
