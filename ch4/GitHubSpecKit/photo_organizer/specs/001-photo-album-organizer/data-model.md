# Data Model: Photo Album Organizer

**Feature**: Photo Album Organizer
**Date**: 2026-06-15

## Entities

### Album

Represents a named, dated collection of photos with a user-defined display order.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Internal surrogate key |
| `name` | TEXT | NOT NULL, 1–100 chars | User-provided album name |
| `date` | TEXT | NOT NULL, ISO 8601 YYYY-MM-DD | Album date used for grouping and default sort |
| `display_order` | REAL | NOT NULL | Fractional index controlling position on main page |
| `cover_photo_id` | INTEGER | REFERENCES photos(id) ON DELETE SET NULL | Cover thumbnail; NULL when album has no photos |
| `created_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | ISO 8601 creation timestamp |

**Validation rules**:
- `name`: 1–100 characters after stripping leading/trailing whitespace; UNIQUE constraint not enforced (users may have two albums with the same name)
- `date`: Valid calendar date string matching `YYYY-MM-DD` pattern
- `display_order`: Positive REAL; managed automatically by fractional indexing — not set directly by the user

**Relationships**:
- One Album has many Photos (1:N, cascade delete)
- One Album has at most one cover Photo (FK into photos, nullable)

---

### Photo

Represents a single image file belonging to exactly one album.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Internal surrogate key |
| `album_id` | INTEGER | NOT NULL, FK → albums(id) ON DELETE CASCADE | Owning album; photo is deleted when album is deleted |
| `filename` | TEXT | NOT NULL | Original file name as provided by the user |
| `filepath` | TEXT | NOT NULL | Relative path under `data/photos/` (e.g., `42/uuid.jpg`) |
| `thumbnail_path` | TEXT | NOT NULL | Relative path under `data/thumbnails/` (e.g., `42/uuid.jpg`) |
| `mime_type` | TEXT | NOT NULL | Validated MIME type derived from magic bytes |
| `size_bytes` | INTEGER | NOT NULL | File size in bytes (must be > 0 and ≤ 20,971,520) |
| `width` | INTEGER | NULL | Original image width in pixels (populated by sharp) |
| `height` | INTEGER | NULL | Original image height in pixels (populated by sharp) |
| `display_order` | REAL | NOT NULL | Fractional index controlling tile order within the album |
| `added_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | ISO 8601 timestamp of when the photo was added |

**Validation rules**:
- `mime_type`: MUST be one of `image/jpeg`, `image/png`, `image/webp`, `image/gif`, `image/heic`, `image/heif`
- `size_bytes`: MUST satisfy `0 < size_bytes ≤ 20,971,520` (20 MB)
- `filepath`: MUST be a relative path within `data/photos/[album_id]/`; path segments MUST NOT contain `..` or begin with `/`

**Relationships**:
- One Photo belongs to exactly one Album (M:1)
- A Photo may be referenced as its album's `cover_photo_id`

---

## Indexes

| Table | Column(s) | Purpose |
|-------|-----------|---------|
| `albums` | `display_order` | ORDER BY for main page album list |
| `albums` | `date` | Grouping albums by date (month/year headings) |
| `photos` | `album_id` | WHERE clause in album view queries |
| `photos` | `(album_id, display_order)` | Ordered photo list per album (covering index) |

---

## State Transitions

### Album `cover_photo_id`

```
Album created (no photos)    → cover_photo_id = NULL
First photo added            → cover_photo_id = photo.id  (auto-set by photo-service)
Cover photo deleted          → cover_photo_id = MIN(display_order) photo in album, or NULL if album is now empty
Album deleted                → cascade deletes all photos; cover_photo_id irrelevant
```

### `display_order` — Fractional Indexing

Used for both albums (main page order) and photos (tile order within album).

```
New item appended
  → display_order = (max existing display_order) + 1000
  → If no items exist: display_order = 1000

Item moved between A and B (A.display_order < B.display_order)
  → new display_order = (A.display_order + B.display_order) / 2

Item moved to start (before current first item F)
  → new display_order = F.display_order - 500  (or 500 if list was empty)

Item moved to end (after current last item L)
  → new display_order = L.display_order + 1000

Gap check after each update
  → IF (successor.display_order - predecessor.display_order) < 0.001
  → Renormalize: UPDATE all rows in ORDER BY display_order, setting display_order = (row_number × 1000)
```

---

## Drizzle ORM Schema

```typescript
// src/lib/db/schema.ts

import { sqliteTable, integer, text, real } from 'drizzle-orm/sqlite-core';
import { sql } from 'drizzle-orm';

export const albums = sqliteTable('albums', {
  id:             integer('id').primaryKey({ autoIncrement: true }),
  name:           text('name').notNull(),
  date:           text('date').notNull(),
  display_order:  real('display_order').notNull(),
  cover_photo_id: integer('cover_photo_id'),
  created_at:     text('created_at').notNull().default(sql`CURRENT_TIMESTAMP`),
});

export const photos = sqliteTable('photos', {
  id:              integer('id').primaryKey({ autoIncrement: true }),
  album_id:        integer('album_id')
                     .notNull()
                     .references(() => albums.id, { onDelete: 'cascade' }),
  filename:        text('filename').notNull(),
  filepath:        text('filepath').notNull(),
  thumbnail_path:  text('thumbnail_path').notNull(),
  mime_type:       text('mime_type').notNull(),
  size_bytes:      integer('size_bytes').notNull(),
  width:           integer('width'),
  height:          integer('height'),
  display_order:   real('display_order').notNull(),
  added_at:        text('added_at').notNull().default(sql`CURRENT_TIMESTAMP`),
});
```

The `cover_photo_id` foreign key is declared separately in the migration SQL
(after both tables exist) to avoid circular reference issues with Drizzle's
schema inference.

---

## Queries

### Main page album list

```sql
SELECT
  a.*,
  p.filepath AS cover_filepath,
  COUNT(ph.id) AS photo_count
FROM albums a
LEFT JOIN photos p ON p.id = a.cover_photo_id
LEFT JOIN photos ph ON ph.album_id = a.id
GROUP BY a.id
ORDER BY a.display_order ASC;
```

### Album photo tile list

```sql
SELECT * FROM photos
WHERE album_id = ?
ORDER BY display_order ASC;
```

Both queries run against indexed columns and complete in < 50 ms for the target
scale (100 albums, 500 photos per album).
