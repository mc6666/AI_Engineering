# API Contracts: Photo Album Organizer

**Feature**: Photo Album Organizer
**Date**: 2026-06-15
**Base URL**: `http://localhost:3000/api`
**Format**: JSON (application/json) for request/response bodies unless noted

---

## Shared Types

### Album Object

```json
{
  "id": 1,
  "name": "Summer Road Trip",
  "date": "2026-06-10",
  "displayOrder": 1000.0,
  "coverPhotoId": 5,
  "coverThumbnailUrl": "/api/photos/5/thumbnail",
  "photoCount": 42,
  "createdAt": "2026-06-15T10:30:00Z"
}
```

| Field | Type | Notes |
|-------|------|-------|
| `id` | integer | Stable identifier |
| `name` | string | 1–100 characters |
| `date` | string | ISO 8601 date (YYYY-MM-DD) |
| `displayOrder` | number | Fractional index; for display only — not sent in write requests |
| `coverPhotoId` | integer \| null | `null` when album has no photos |
| `coverThumbnailUrl` | string \| null | URL to thumbnail endpoint; `null` when no cover |
| `photoCount` | integer | Number of photos currently in the album |
| `createdAt` | string | ISO 8601 datetime |

---

### Photo Object

```json
{
  "id": 5,
  "albumId": 1,
  "filename": "DSC_0042.jpg",
  "imageUrl": "/api/photos/5/image",
  "thumbnailUrl": "/api/photos/5/thumbnail",
  "mimeType": "image/jpeg",
  "sizeBytes": 4194304,
  "width": 4000,
  "height": 3000,
  "displayOrder": 1000.0,
  "addedAt": "2026-06-15T10:35:00Z"
}
```

| Field | Type | Notes |
|-------|------|-------|
| `id` | integer | Stable identifier |
| `albumId` | integer | Owning album |
| `filename` | string | Original file name |
| `imageUrl` | string | URL to full-size image endpoint |
| `thumbnailUrl` | string | URL to 400×400 JPEG thumbnail endpoint |
| `mimeType` | string | Validated MIME type |
| `sizeBytes` | integer | File size in bytes |
| `width` | integer \| null | Original width in pixels |
| `height` | integer \| null | Original height in pixels |
| `displayOrder` | number | Fractional tile order within album |
| `addedAt` | string | ISO 8601 datetime |

---

### Error Object

```json
{
  "error": "VALIDATION_ERROR",
  "message": "File type 'application/pdf' is not a supported image format.",
  "field": "file"
}
```

| Code | HTTP Status | When used |
|------|-------------|-----------|
| `VALIDATION_ERROR` | 422 | Input fails validation (name too long, bad date, unsupported file type) |
| `NOT_FOUND` | 404 | Album or photo does not exist |
| `PAYLOAD_TOO_LARGE` | 413 | File exceeds 20 MB limit |
| `INTERNAL_ERROR` | 500 | Unexpected server-side failure |

The `field` property is present only for `VALIDATION_ERROR` and names the
request field that failed (e.g., `"name"`, `"date"`, `"file"`).

---

## Albums Endpoints

### `GET /api/albums`

Returns all albums ordered by `display_order` ascending.

**Response 200**

```json
{
  "albums": [Album, ...]
}
```

Albums are returned in display order. The client groups them by `date`
(year-month) for the date-grouped UI headings.

---

### `POST /api/albums`

Creates a new album. The server assigns `display_order = (max existing + 1000)`
or `1000` if no albums exist.

**Request body**

```json
{
  "name": "Birthday Party 2026",
  "date": "2026-06-10"
}
```

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `name` | string | yes | 1–100 characters (after trim) |
| `date` | string | yes | ISO 8601 date YYYY-MM-DD |

**Response 201**

```json
{ "album": Album }
```

**Response 422** — validation failure

```json
{ "error": "VALIDATION_ERROR", "message": "Name must be between 1 and 100 characters.", "field": "name" }
```

---

### `GET /api/albums/[id]`

Returns a single album with its full photo list.

**Response 200**

```json
{
  "album": Album,
  "photos": [Photo, ...]
}
```

Photos are ordered by `display_order` ascending.

**Response 404**

```json
{ "error": "NOT_FOUND", "message": "Album not found." }
```

---

### `PUT /api/albums/[id]`

Updates one or both of `name` and `date`. Only provided fields are updated.

**Request body**

```json
{
  "name": "Updated Album Name",
  "date": "2026-07-04"
}
```

Both fields are optional but at least one must be present.

**Response 200**

```json
{ "album": Album }
```

**Response 404** — album not found.

**Response 422** — validation failure on provided fields.

---

### `DELETE /api/albums/[id]`

Deletes an album. Cascades to delete all its photos from the database and
removes original image files and thumbnails from disk.

**Response 204** — No content.

**Response 404** — album not found.

---

### `POST /api/albums/[id]/reorder`

Persists the new position of an album after a drag-and-drop interaction.
The server computes `display_order` from the provided neighbour orders.

**Request body**

```json
{
  "predecessorOrder": 2000.0,
  "successorOrder": 3000.0
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `predecessorOrder` | number | conditional | The display_order of the album immediately before the moved item; omit if moved to the start of the list |
| `successorOrder` | number | conditional | The display_order of the album immediately after the moved item; omit if moved to the end of the list |

At least one of `predecessorOrder` or `successorOrder` MUST be provided.

**Server computation**:
- Both provided: `newOrder = (predecessorOrder + successorOrder) / 2`
- Only `predecessorOrder`: `newOrder = predecessorOrder + 1000`
- Only `successorOrder`: `newOrder = successorOrder - 500`
- If the computed gap to any neighbour < 0.001: server renormalizes all albums
  to `rowIndex × 1000` then returns the updated order

**Response 200**

```json
{ "album": Album }
```

**Response 404** — album not found.

**Response 422** — neither predecessor nor successor provided.

---

### `POST /api/albums/[id]/photos`

Adds a photo to an album. Accepts `multipart/form-data`.

**Request**: `Content-Type: multipart/form-data`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `file` | File | yes | Image file; validated by magic bytes server-side |

**Processing order**:
1. Read first 12 bytes → validate magic bytes → reject if not a supported format
2. Check `size_bytes ≤ 20,971,520`
3. Save original to `data/photos/[album-id]/[uuid].[ext]`
4. Generate 400×400 JPEG thumbnail via `sharp` → `data/thumbnails/[album-id]/[uuid].jpg`
5. Extract width and height from `sharp` metadata
6. Insert photo row with `display_order = (max in album + 1000)` or `1000`
7. If first photo in album: UPDATE album SET cover_photo_id = new photo id

**Response 201**

```json
{ "photo": Photo }
```

**Response 404** — album not found.

**Response 413** — file exceeds 20 MB.

**Response 422** — unsupported file type.

```json
{ "error": "VALIDATION_ERROR", "message": "File type is not a supported image format. Supported types: JPEG, PNG, WebP, GIF, HEIC.", "field": "file" }
```

---

## Photos Endpoints

### `DELETE /api/photos/[id]`

Removes a photo from its album. Deletes the original file and thumbnail from
disk. If the photo was the album's cover, the next photo by `display_order`
becomes the new cover (or cover is set to NULL if album is now empty).

**Response 204** — No content.

**Response 404** — photo not found.

---

### `GET /api/photos/[id]/image`

Streams the original image file.

**Response 200**

- Body: raw image bytes
- `Content-Type`: matches photo's `mime_type` (e.g., `image/jpeg`)
- `Cache-Control: public, max-age=31536000, immutable`
- `Content-Length`: file size in bytes

**Response 404** — photo record or file not found.

---

### `GET /api/photos/[id]/thumbnail`

Streams the generated 400×400 JPEG thumbnail.

**Response 200**

- Body: JPEG bytes
- `Content-Type: image/jpeg`
- `Cache-Control: public, max-age=31536000, immutable`

**Response 404** — photo record or thumbnail file not found.

---

## Error Handling Summary

All endpoints return JSON error objects (see Error Object above) on failure.
HTTP status codes follow REST conventions:

| Situation | Status |
|-----------|--------|
| Successful read | 200 |
| Successful create | 201 |
| Successful delete | 204 |
| Validation failure | 422 |
| Not found | 404 |
| File too large | 413 |
| Unexpected error | 500 |
