from pathlib import Path
import aiosqlite

_connection: aiosqlite.Connection | None = None

_SCHEMA_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS albums (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        label          TEXT    NOT NULL,
        date           TEXT    NOT NULL,
        cover_photo_id INTEGER REFERENCES photos(id) ON DELETE SET NULL,
        display_order  INTEGER NOT NULL DEFAULT 0,
        created_at     TEXT    NOT NULL
    )""",
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_albums_date ON albums (date)",
    "CREATE INDEX IF NOT EXISTS idx_albums_display_order ON albums (display_order)",
    """CREATE TABLE IF NOT EXISTS photos (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        filename       TEXT    NOT NULL,
        file_path      TEXT    NOT NULL,
        date_taken     TEXT,
        import_date    TEXT    NOT NULL,
        file_size      INTEGER,
        album_id       INTEGER NOT NULL REFERENCES albums(id) ON DELETE CASCADE,
        thumbnail_path TEXT
    )""",
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_photos_file_path ON photos (file_path)",
    "CREATE INDEX IF NOT EXISTS idx_photos_album_id ON photos (album_id)",
    "CREATE INDEX IF NOT EXISTS idx_photos_date_taken ON photos (date_taken)",
]


async def init(db_path: str = "data/photo_organizer.db") -> None:
    global _connection
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    _connection = await aiosqlite.connect(db_path)
    _connection.row_factory = aiosqlite.Row
    for statement in _SCHEMA_STATEMENTS:
        await _connection.execute(statement)
    await _connection.commit()


def get_connection() -> aiosqlite.Connection:
    if _connection is None:
        raise RuntimeError("Database not initialized. Call db.init() first.")
    return _connection


async def close() -> None:
    global _connection
    if _connection:
        await _connection.close()
        _connection = None
