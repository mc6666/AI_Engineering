import pytest
from pathlib import Path
from PIL import Image
from src.services import thumbnail_service


@pytest.fixture()
def tmp_thumb_dir(tmp_path, monkeypatch):
    thumb_dir = tmp_path / "thumbnails"
    thumb_dir.mkdir()
    monkeypatch.setattr(thumbnail_service, "THUMBNAIL_DIR", thumb_dir)
    return thumb_dir


def _make_jpeg(path: Path, size: tuple = (800, 600)) -> None:
    img = Image.new("RGB", size, color=(120, 80, 200))
    img.save(str(path), "JPEG")


async def test_generate_creates_thumbnail(tmp_path, tmp_thumb_dir):
    src = tmp_path / "photo.jpg"
    _make_jpeg(src)
    result = await thumbnail_service.generate(1, str(src))
    assert Path(result).exists()


async def test_generate_thumbnail_is_256x256(tmp_path, tmp_thumb_dir):
    src = tmp_path / "photo.jpg"
    _make_jpeg(src, size=(1200, 800))
    result = await thumbnail_service.generate(2, str(src))
    with Image.open(result) as img:
        assert img.size == (256, 256)


async def test_generate_is_idempotent(tmp_path, tmp_thumb_dir):
    src = tmp_path / "photo.jpg"
    _make_jpeg(src)
    r1 = await thumbnail_service.generate(3, str(src))
    r2 = await thumbnail_service.generate(3, str(src))
    assert r1 == r2


async def test_generate_output_is_jpeg(tmp_path, tmp_thumb_dir):
    src = tmp_path / "photo.png"
    img = Image.new("RGB", (200, 200), color=(0, 128, 255))
    img.save(str(src), "PNG")
    result = await thumbnail_service.generate(4, str(src))
    with Image.open(result) as out:
        assert out.format == "JPEG"
