import datetime
from src.models.album import Album
from src.services import db


def _row_to_album(row) -> Album:
    return Album(
        id=row["id"],
        label=row["label"],
        date=row["date"],
        cover_photo_id=row["cover_photo_id"],
        display_order=row["display_order"],
        created_at=row["created_at"],
    )


async def get_all_albums() -> list[Album]:
    conn = db.get_connection()
    async with conn.execute("SELECT * FROM albums ORDER BY display_order ASC") as cursor:
        rows = await cursor.fetchall()
    return [_row_to_album(r) for r in rows]


async def get_album_by_id(album_id: int) -> Album | None:
    conn = db.get_connection()
    async with conn.execute("SELECT * FROM albums WHERE id = ?", (album_id,)) as cursor:
        row = await cursor.fetchone()
    return _row_to_album(row) if row else None


async def get_or_create_by_date(date_str: str) -> Album:
    conn = db.get_connection()
    async with conn.execute("SELECT * FROM albums WHERE date = ?", (date_str,)) as cursor:
        row = await cursor.fetchone()
    if row:
        return _row_to_album(row)

    async with conn.execute("SELECT COALESCE(MAX(display_order) + 1, 0) FROM albums") as cursor:
        next_order_row = await cursor.fetchone()
    next_order = next_order_row[0] if next_order_row else 0

    now = datetime.datetime.now().isoformat(sep="T", timespec="seconds")
    async with conn.execute(
        "INSERT INTO albums (label, date, display_order, created_at) VALUES (?, ?, ?, ?)",
        (date_str, date_str, next_order, now),
    ) as cursor:
        album_id = cursor.lastrowid
    await conn.commit()
    return Album(id=album_id, label=date_str, date=date_str, display_order=next_order, created_at=now)


async def update_cover_photo(album_id: int, photo_id: int) -> None:
    """Set cover_photo_id only if it has not been set yet."""
    conn = db.get_connection()
    await conn.execute(
        "UPDATE albums SET cover_photo_id = ? WHERE id = ? AND cover_photo_id IS NULL",
        (photo_id, album_id),
    )
    await conn.commit()


async def update_label(album_id: int, new_label: str) -> Album | None:
    conn = db.get_connection()
    await conn.execute("UPDATE albums SET label = ? WHERE id = ?", (new_label, album_id))
    await conn.commit()
    return await get_album_by_id(album_id)


async def update_display_order(ordered_ids: list[int]) -> None:
    """Reassign display_order as contiguous integers matching the position in ordered_ids."""
    conn = db.get_connection()
    for index, album_id in enumerate(ordered_ids):
        await conn.execute(
            "UPDATE albums SET display_order = ? WHERE id = ?", (index, album_id)
        )
    await conn.commit()
