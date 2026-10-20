import os
import tempfile
import pytest
from src.services import db, album_service


@pytest.fixture(autouse=True)
async def isolated_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    await db.init(db_path)
    yield
    await db.close()
    os.unlink(db_path)


async def _seed_album(label: str, date: str, display_order: int = 0) -> int:
    conn = db.get_connection()
    async with conn.execute(
        "INSERT INTO albums (label, date, display_order, created_at) VALUES (?, ?, ?, ?)",
        (label, date, display_order, "2024-01-01T00:00:00"),
    ) as cursor:
        album_id = cursor.lastrowid
    await conn.commit()
    return album_id


# --- get_all_albums ---

async def test_get_all_albums_empty():
    albums = await album_service.get_all_albums()
    assert albums == []


async def test_get_all_albums_returns_ordered_by_display_order():
    await _seed_album("C", "2024-03-01", display_order=2)
    await _seed_album("A", "2024-01-01", display_order=0)
    await _seed_album("B", "2024-02-01", display_order=1)
    albums = await album_service.get_all_albums()
    assert [a.label for a in albums] == ["A", "B", "C"]


async def test_get_album_by_id_found():
    album_id = await _seed_album("Test", "2024-06-15", display_order=0)
    album = await album_service.get_album_by_id(album_id)
    assert album is not None
    assert album.label == "Test"
    assert album.date == "2024-06-15"


async def test_get_album_by_id_not_found():
    album = await album_service.get_album_by_id(999)
    assert album is None


# --- get_or_create_by_date ---

async def test_get_or_create_by_date_creates_new():
    album = await album_service.get_or_create_by_date("2024-06-15")
    assert album.date == "2024-06-15"
    assert album.label == "2024-06-15"
    assert album.id is not None


async def test_get_or_create_by_date_returns_existing():
    album1 = await album_service.get_or_create_by_date("2024-06-15")
    album2 = await album_service.get_or_create_by_date("2024-06-15")
    assert album1.id == album2.id


async def test_get_or_create_increments_display_order():
    a1 = await album_service.get_or_create_by_date("2024-01-01")
    a2 = await album_service.get_or_create_by_date("2024-01-02")
    assert a2.display_order == a1.display_order + 1


# --- update_label ---

async def test_update_label():
    album_id = await _seed_album("2024-06-15", "2024-06-15")
    updated = await album_service.update_label(album_id, "Summer Vacation")
    assert updated.label == "Summer Vacation"


# --- update_display_order ---

async def test_update_display_order():
    id1 = await _seed_album("A", "2024-01-01", display_order=0)
    id2 = await _seed_album("B", "2024-02-01", display_order=1)
    id3 = await _seed_album("C", "2024-03-01", display_order=2)
    await album_service.update_display_order([id3, id1, id2])
    albums = await album_service.get_all_albums()
    assert albums[0].id == id3
    assert albums[1].id == id1
    assert albums[2].id == id2


async def test_update_display_order_no_gaps():
    id1 = await _seed_album("A", "2024-01-01", display_order=5)
    id2 = await _seed_album("B", "2024-02-01", display_order=10)
    await album_service.update_display_order([id2, id1])
    albums = await album_service.get_all_albums()
    assert albums[0].display_order == 0
    assert albums[1].display_order == 1
