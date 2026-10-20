"""Tests for AlbumService.update_display_order — Phase 6 / US3."""
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


async def _seed(label: str, date: str, order: int = 0) -> int:
    conn = db.get_connection()
    async with conn.execute(
        "INSERT INTO albums (label, date, display_order, created_at) VALUES (?, ?, ?, ?)",
        (label, date, order, "2024-01-01T00:00:00"),
    ) as cursor:
        aid = cursor.lastrowid
    await conn.commit()
    return aid


async def test_update_display_order_sets_correct_positions():
    id1 = await _seed("A", "2024-01-01", 0)
    id2 = await _seed("B", "2024-02-01", 1)
    id3 = await _seed("C", "2024-03-01", 2)
    await album_service.update_display_order([id3, id1, id2])
    albums = await album_service.get_all_albums()
    assert albums[0].id == id3
    assert albums[1].id == id1
    assert albums[2].id == id2


async def test_update_display_order_produces_contiguous_values():
    id1 = await _seed("A", "2024-01-01", 10)
    id2 = await _seed("B", "2024-02-01", 20)
    await album_service.update_display_order([id2, id1])
    albums = await album_service.get_all_albums()
    orders = [a.display_order for a in albums]
    assert orders == [0, 1]


async def test_update_display_order_persists_across_queries():
    id1 = await _seed("X", "2024-05-01", 0)
    id2 = await _seed("Y", "2024-06-01", 1)
    await album_service.update_display_order([id2, id1])
    # Re-fetch to confirm persistence
    albums = await album_service.get_all_albums()
    assert albums[0].id == id2
    assert albums[1].id == id1
