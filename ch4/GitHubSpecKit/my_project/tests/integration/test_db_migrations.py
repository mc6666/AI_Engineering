import os
import tempfile
import pytest
from src.services import db


@pytest.fixture(autouse=True)
async def isolated_db():
    """Each test gets a fresh temporary database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    await db.init(db_path)
    yield
    await db.close()
    os.unlink(db_path)


async def test_albums_table_exists():
    conn = db.get_connection()
    async with conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='albums'"
    ) as cursor:
        row = await cursor.fetchone()
    assert row is not None


async def test_photos_table_exists():
    conn = db.get_connection()
    async with conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='photos'"
    ) as cursor:
        row = await cursor.fetchone()
    assert row is not None


async def test_albums_unique_date_index_exists():
    conn = db.get_connection()
    async with conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_albums_date'"
    ) as cursor:
        row = await cursor.fetchone()
    assert row is not None


async def test_photos_unique_file_path_index_exists():
    conn = db.get_connection()
    async with conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_photos_file_path'"
    ) as cursor:
        row = await cursor.fetchone()
    assert row is not None


async def test_albums_date_unique_constraint():
    conn = db.get_connection()
    await conn.execute(
        "INSERT INTO albums (label, date, display_order, created_at) VALUES (?, ?, ?, ?)",
        ("2024-01-01", "2024-01-01", 0, "2024-01-01T00:00:00"),
    )
    await conn.commit()
    import aiosqlite
    with pytest.raises(aiosqlite.IntegrityError):
        await conn.execute(
            "INSERT INTO albums (label, date, display_order, created_at) VALUES (?, ?, ?, ?)",
            ("2024-01-01", "2024-01-01", 1, "2024-01-01T00:00:01"),
        )
        await conn.commit()
