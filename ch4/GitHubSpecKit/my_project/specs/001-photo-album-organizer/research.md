# Research: Photo Album Organizer

**Feature**: 001-photo-album-organizer
**Date**: 2026-06-14

---

## Decision 1: NiceGUI as UI Framework

**Decision**: Use NiceGUI ≥1.4 as the sole UI framework.

**Rationale**: NiceGUI runs a FastAPI/Starlette server locally and renders UI using Vue.js/Quasar
in the browser. It handles routing, component lifecycle, async I/O, and static file serving out
of the box. This eliminates the need for a separate frontend build pipeline and produces a
single-process Python application appropriate for a local desktop tool.

**Key capabilities used**:
- `@ui.page('/')` and `@ui.page('/album/{id}')` for client-side navigation
- `app.add_media_files('/thumbnails', 'thumbnails/')` to serve generated thumbnails as static media
- `app.add_media_files('/originals', ...)` is not used — original images are only loaded in the
  lightbox via a dynamic route that streams the file from its absolute path
- `ui.notify()` for consistent toast-style error and info messages
- `ui.upload()` for file picker (browser security limits: full path not exposed, so the upload
  handler receives file bytes + filename; files are indexed by content, not by path)

**Note on file selection**: Browser security prevents JavaScript from reading the full filesystem
path of a selected file. The chosen approach is `ui.upload(multiple=True)` — the user selects
image files, the server receives the bytes, writes them to a configurable `photos/` storage
directory, and records the stored path in SQLite. This is the practical interpretation of "images
are not uploaded anywhere": photos are not sent to a remote server; they are stored locally.

**Alternatives considered**:
- Flask + Jinja2: Would require a separate frontend build for drag-and-drop; more boilerplate.
- NiceGUI native mode (pywebview): Provides true filesystem access, but adds a native dependency
  and complicates testing. Deferred to a future version.
- Tkinter: No web-quality tile layout or drag-and-drop support.

---

## Decision 2: EXIF Metadata Extraction

**Decision**: Use `Pillow` (`PIL.ExifTags`, `PIL.Image._getexif()`) for EXIF reading.

**Rationale**: Pillow is already required for thumbnail generation, so no additional dependency
is introduced. The `DateTimeOriginal` EXIF tag (ID 36867) provides the most accurate capture
date. Fallback chain: `DateTimeOriginal` → `DateTime` (tag 306) → file modification time at
import → today's date (with user notification).

**Date parsing**: EXIF dates use format `YYYY:MM:DD HH:MM:SS`. These are converted to ISO
`YYYY-MM-DD` for album grouping and storage.

**Alternatives considered**:
- `exifread` library: More EXIF features but an extra dependency; Pillow sufficient for date
  extraction.
- `piexif`: Write-only focus; overkill for read-only metadata extraction.

---

## Decision 3: Drag-and-Drop Album Reordering

**Decision**: Integrate SortableJS via NiceGUI's JavaScript interop.

**Rationale**: NiceGUI 1.4 does not include a built-in sortable list component. SortableJS is
a mature, well-tested library (MIT license) with touch support. NiceGUI exposes
`ui.add_head_html()` to inject the SortableJS CDN script and `ui.run_javascript()` /
`app.on_connect()` to initialize the sortable instance. When the user drops an album card, a
JavaScript `onEnd` callback fires `ui.run_javascript(...)` that calls a Python-bound function
via `app.call_python()` or NiceGUI's event system, passing the new order as a list of album IDs.
The Python handler persists the new `display_order` values to SQLite.

**Implementation pattern**:
```
1. Render album cards with data-id attributes containing album IDs
2. After page load: new Sortable(container, { onEnd: sendOrderToServer })
3. sendOrderToServer: collect data-id values, POST to /api/albums/reorder
4. Python handler: album_service.update_display_order(ordered_ids)
```

**Touch support**: SortableJS handles touch events natively; no additional code needed.

**Alternatives considered**:
- Quasar `QSortable`: Not directly accessible from NiceGUI's Python API in v1.4.
- Pure CSS drag-and-drop: No persistence mechanism without JavaScript callbacks.
- Manual up/down buttons: Functional but does not meet the drag-and-drop requirement.

---

## Decision 4: Thumbnail Generation and Caching

**Decision**: Generate thumbnails with Pillow at import time; cache as JPEG in `thumbnails/`
directory; serve via NiceGUI static files.

**Rationale**: Pre-generating thumbnails at import time ensures the album tile grid (SC-004:
100 photos < 3 seconds) and main page (SC-002: 50 albums < 3 seconds) meet performance targets
without on-demand processing. Thumbnail size: 256×256 px (square crop from center). Storage
cost is low (~10–30 KB per thumbnail).

**Thumbnail path convention**: `thumbnails/{photo_id}.jpg` — keyed by SQLite `photos.id` to
avoid filename collision. NiceGUI serves the directory at `/thumbnails/` via
`app.add_media_files('/thumbnails', 'thumbnails/')`.

**Regeneration**: If a thumbnail is missing on page load (e.g., cache cleared), it is
regenerated on the fly. A background task can re-scan missing thumbnails at startup.

**Alternatives considered**:
- On-demand thumbnail generation: Causes unacceptable delay on first album open (violates SC-004).
- Storing thumbnails in SQLite as BLOBs: Poor performance for large collections; filesystem
  caching is faster and more standard.

---

## Decision 5: SQLite Access Pattern

**Decision**: Use `aiosqlite` for async SQLite access throughout, matching NiceGUI's async event
loop.

**Rationale**: NiceGUI runs on an asyncio event loop (via Starlette/uvicorn). Synchronous SQLite
calls (`sqlite3`) would block the event loop and cause UI freezes during database operations.
`aiosqlite` wraps `sqlite3` in a thread pool, keeping the event loop responsive.

**Connection management**: A single persistent connection is opened at app startup and closed on
shutdown, managed in `src/services/db.py`. Schema creation and migrations run at startup.

**Alternatives considered**:
- SQLAlchemy async: More features but significant overhead for a simple local app with two
  tables. `aiosqlite` direct SQL is sufficient and keeps the dependency footprint small.
- SQLite with threading: Python's `sqlite3` with `check_same_thread=False` is an alternative
  but requires manual thread synchronization; `aiosqlite` is cleaner for an async app.

---

## Decision 6: Original Image Serving for Lightbox

**Decision**: Serve original images via a NiceGUI dynamic API route that reads the file from
its absolute stored path.

**Rationale**: `app.add_media_files()` serves a single static directory. Since all photos are
stored in the configurable `photos/` directory (per Decision 1), a single static mount is
sufficient: `app.add_media_files('/photos', 'photos/')`. The lightbox `ui.image` uses the
relative URL `/photos/{filename}` to load the full-resolution original.

**Alternatives considered**:
- Serving originals from arbitrary filesystem paths: Requires a dynamic route with path
  sanitization to prevent directory traversal. Avoided by constraining storage to a single
  directory.

---

## Summary of Resolved Clarifications

| Topic | Decision |
|-------|----------|
| Photo storage | Photos stored in local `photos/` directory (not remote); metadata in SQLite |
| File selection mechanism | `ui.upload()` — browser-based file picker; bytes received by server |
| EXIF date fallback | DateTimeOriginal → DateTime → file mtime → today's date |
| Drag-and-drop | SortableJS via NiceGUI JavaScript interop |
| Thumbnail strategy | Pillow, 256×256 px, pre-generated at import, cached in `thumbnails/` |
| SQLite access | aiosqlite (async), single connection, schema at startup |
| Original image serving | Static mount of `photos/` directory via NiceGUI |
