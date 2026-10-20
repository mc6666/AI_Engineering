# Data Model: Photo Album Organizer

**Feature**: 001-photo-album-organizer
**Date**: 2026-06-14
**Storage**: SQLite (local file `data/photo_organizer.db`)

---

## Entities

### Album

Represents a named grouping of photos associated with a specific calendar date.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Surrogate key |
| `label` | TEXT | NOT NULL | Display name; defaults to ISO date string; user-renameable |
| `date` | TEXT | NOT NULL | ISO date `YYYY-MM-DD`; the grouping key for auto-assignment |
| `cover_photo_id` | INTEGER | NULLABLE, FK → photos.id | First photo in album by default; updated on photo import |
| `display_order` | INTEGER | NOT NULL, DEFAULT 0 | Custom sort position on main page; lower = first |
| `created_at` | TEXT | NOT NULL | ISO datetime `YYYY-MM-DDTHH:MM:SS` of album creation |

**Invariants**:
- `date` is unique across all albums (one album per calendar date).
- Albums are never nested; there is no `parent_album_id` column.
- `display_order` values are reassigned as contiguous integers (0, 1, 2, …) after every reorder
  operation to avoid gaps.

**Indexes**:
- UNIQUE on `date` — enforces one album per date.
- INDEX on `display_order` — supports fast ordered fetch for main page rendering.

---

### Photo

Represents an image file imported into the system.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Surrogate key |
| `filename` | TEXT | NOT NULL | Original filename as stored in `photos/` directory |
| `file_path` | TEXT | NOT NULL, UNIQUE | Relative path within `photos/` directory (e.g., `abc123_IMG_001.jpg`) |
| `date_taken` | TEXT | NULLABLE | ISO date `YYYY-MM-DD` from EXIF; NULL if not available |
| `import_date` | TEXT | NOT NULL | ISO datetime when the photo was imported |
| `file_size` | INTEGER | NULLABLE | File size in bytes |
| `album_id` | INTEGER | NOT NULL, FK → albums.id | The album this photo belongs to |
| `thumbnail_path` | TEXT | NULLABLE | Relative path to generated thumbnail (e.g., `thumbnails/42.jpg`) |

**Invariants**:
- Each photo belongs to exactly one album (`album_id` is non-nullable).
- `file_path` is unique — the same physical file cannot be imported twice under different records.
- Photos are never reassigned to a different album after import (v1 scope).
- `thumbnail_path` is set after thumbnail generation; it may be NULL transiently during import.

**Indexes**:
- UNIQUE on `file_path`.
- INDEX on `album_id` — supports fast fetch of all photos in an album.
- INDEX on `date_taken` — supports potential future filtering by date.

---

## Schema DDL

```sql
CREATE TABLE IF NOT EXISTS albums (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    label          TEXT    NOT NULL,
    date           TEXT    NOT NULL,
    cover_photo_id INTEGER REFERENCES photos(id) ON DELETE SET NULL,
    display_order  INTEGER NOT NULL DEFAULT 0,
    created_at     TEXT    NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_albums_date
    ON albums (date);

CREATE INDEX IF NOT EXISTS idx_albums_display_order
    ON albums (display_order);

CREATE TABLE IF NOT EXISTS photos (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    filename       TEXT    NOT NULL,
    file_path      TEXT    NOT NULL,
    date_taken     TEXT,
    import_date    TEXT    NOT NULL,
    file_size      INTEGER,
    album_id       INTEGER NOT NULL REFERENCES albums(id) ON DELETE CASCADE,
    thumbnail_path TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_photos_file_path
    ON photos (file_path);

CREATE INDEX IF NOT EXISTS idx_photos_album_id
    ON photos (album_id);

CREATE INDEX IF NOT EXISTS idx_photos_date_taken
    ON photos (date_taken);
```

---

## Relationships

```
albums (1) ──────────── (N) photos
  id ◄──────────── album_id

albums.cover_photo_id ──► photos.id   (nullable reference to the cover photo)
```

- One album contains zero or more photos.
- Each photo belongs to exactly one album.
- An album's `cover_photo_id` is a soft reference to one of its own photos (for display on the
  main page); it is set to NULL if the referenced photo is deleted (ON DELETE SET NULL).
- Deleting an album cascades to delete all its photos (ON DELETE CASCADE on `photos.album_id`).

---

## State Transitions

### Photo Import Flow

```
File selected by user
       │
       ▼
Validate file format (JPEG/PNG/GIF/WEBP)
       │ invalid → reject with error message
       ▼
Extract EXIF date_taken
       │ no EXIF → use today's date + notify user
       ▼
Look up album by date
       │ not found → create new album (label = date, display_order = max + 1)
       ▼
Store file in photos/ directory with collision-safe filename
       │
       ▼
Insert photo record in SQLite
       │
       ▼
Generate thumbnail (256×256 px JPEG) → store in thumbnails/
       │
       ▼
Update photo.thumbnail_path
       │
       ▼
Update album.cover_photo_id if album had no cover
       │
       ▼
Import complete
```

### Album Reorder Flow

```
User releases drag on main page
       │
       ▼
SortableJS fires onEnd → collect ordered album IDs from DOM
       │
       ▼
POST /api/albums/reorder { ordered_ids: [...] }
       │
       ▼
album_service.update_display_order(ordered_ids)
  → UPDATE albums SET display_order = ? WHERE id = ?  (per item in list)
       │
       ▼
200 OK → no page refresh needed
```

---

## Data Integrity Rules

1. An album's `date` field MUST be a valid ISO date (`YYYY-MM-DD`).
2. A photo's `date_taken` field, if set, MUST be a valid ISO date.
3. `display_order` values across all albums MUST form a contiguous sequence starting at 0
   after any reorder operation.
4. `cover_photo_id` MUST reference a photo whose `album_id` matches the album's own `id`.
5. `file_path` values MUST be relative to the `photos/` directory root (no absolute paths in DB).
