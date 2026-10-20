import io
import os
import tempfile
import pytest
from pathlib import Path
from PIL import Image
from src.services import db, photo_service, album_service, thumbnail_service


@pytest.fixture(autouse=True)
async def isolated_env(tmp_path, monkeypatch):
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    await db.init(db_path)
    monkeypatch.setattr(photo_service, "PHOTOS_DIR", tmp_path / "photos")
    monkeypatch.setattr(thumbnail_service, "THUMBNAIL_DIR", tmp_path / "thumbnails")
    yield
    await db.close()
    os.unlink(db_path)


def _jpeg(color=(100, 150, 200)) -> bytes:
    img = Image.new("RGB", (200, 150), color=color)
    buf = io.BytesIO()
    img.save(buf, "JPEG")
    return buf.getvalue()


def _png(color=(200, 100, 50)) -> bytes:
    img = Image.new("RGB", (150, 150), color=color)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


async def test_import_three_photos_creates_album():
    await photo_service.import_photo("a.jpg", _jpeg())
    await photo_service.import_photo("b.jpg", _jpeg((200, 100, 50)))
    await photo_service.import_photo("c.png", _png())
    albums = await album_service.get_all_albums()
    # All lack EXIF → today's date → one album
    assert len(albums) == 1
    photos = await photo_service.get_photos_by_album(albums[0].id)
    assert len(photos) == 3


async def test_thumbnails_generated_on_import(tmp_path):
    photo = await photo_service.import_photo("img.jpg", _jpeg())
    assert photo.thumbnail_path is not None
    assert Path(photo.thumbnail_path).exists()


async def test_album_cover_set_after_import():
    photo = await photo_service.import_photo("cover.jpg", _jpeg())
    album = await album_service.get_album_by_id(photo.album_id)
    assert album.cover_photo_id == photo.id


async def test_second_photo_same_date_no_duplicate_album():
    p1 = await photo_service.import_photo("x.jpg", _jpeg())
    p2 = await photo_service.import_photo("y.jpg", _jpeg((50, 60, 70)))
    assert p1.album_id == p2.album_id
    albums = await album_service.get_all_albums()
    assert len(albums) == 1


async def test_invalid_file_rejected():
    with pytest.raises(ValueError, match="not a supported image format"):
        await photo_service.import_photo("malware.exe", b"MZ\x90\x00fake exe")
