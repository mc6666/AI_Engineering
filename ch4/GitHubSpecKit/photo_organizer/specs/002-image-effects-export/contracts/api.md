# API Contracts: Image Processing with Special Effects & Export

**Feature**: Image Effects & Export
**Date**: 2026-06-17

These are the three new API routes added by this feature. All existing routes from spec 001 are unchanged.

---

## POST `/api/photos/[id]/process`

Process a single photo with an effect chain and stream the result as a downloadable image.

### Request

```
POST /api/photos/42/process
Content-Type: application/json
```

```json
{
  "effects": [
    { "type": "grayscale", "intensity": 100 },
    { "type": "blur", "intensity": 30 }
  ],
  "format": "jpeg"
}
```

**Body fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `effects` | `EffectParam[]` | Yes | Ordered list of effects to apply; 0–5 items |
| `format` | `"jpeg"` \| `"png"` | Yes | Output file format |

**EffectParam fields**:

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `type` | `EffectType` | Yes | One of: `grayscale`, `sepia`, `vintage`, `blur`, `sharpen`, `brightness`, `contrast`, `saturation` |
| `intensity` | integer | Yes | `0–100` (inclusive); ignored for `vintage` |

### Responses

**200 OK** — processed image binary

```
Content-Type: image/jpeg
Content-Disposition: attachment; filename="photo-42-processed.jpg"
Cache-Control: no-store
```

Body: Raw image bytes (JPEG or PNG depending on `format`).

**400 Bad Request** — validation failure

```json
{
  "error": "VALIDATION_ERROR",
  "message": "effects must have at most 5 items",
  "field": "effects"
}
```

Common validation errors:
- `effects` length > 5
- Unknown `type` value
- `intensity` outside `[0, 100]`
- `format` not `jpeg` or `png`

**404 Not Found** — photo id does not exist

```json
{ "error": "NOT_FOUND", "message": "Photo not found" }
```

**500 Internal Server Error** — sharp processing failure

```json
{ "error": "INTERNAL_ERROR", "message": "Image processing failed" }
```

---

## POST `/api/photos/export`

Batch-process a selection of photos and stream a ZIP archive containing all processed images.

### Request

```
POST /api/photos/export
Content-Type: application/json
```

```json
{
  "photoIds": [1, 5, 12, 33],
  "effects": [
    { "type": "sepia", "intensity": 80 }
  ],
  "format": "png"
}
```

**Body fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `photoIds` | `number[]` | Yes | Non-empty list of photo IDs to export |
| `effects` | `EffectParam[]` | Yes | Uniform effect chain applied to every photo; 0–5 items |
| `format` | `"jpeg"` \| `"png"` | Yes | Output format for all photos in the archive |

### Responses

**200 OK** — ZIP archive stream

```
Content-Type: application/zip
Content-Disposition: attachment; filename="photos-export.zip"
Cache-Control: no-store
```

Body: Streaming ZIP archive. Entry names inside the archive follow the pattern `{photo_id}-{original_filename}.{ext}` (e.g., `42-vacation.jpg`).

**400 Bad Request** — validation failure

```json
{
  "error": "VALIDATION_ERROR",
  "message": "photoIds must be a non-empty array",
  "field": "photoIds"
}
```

**404 Not Found** — one or more photo IDs not found

```json
{
  "error": "NOT_FOUND",
  "message": "Photos not found: 5, 12"
}
```

**500 Internal Server Error** — processing or ZIP failure

```json
{ "error": "INTERNAL_ERROR", "message": "Export failed" }
```

---

## POST `/api/albums/[id]/export`

Batch-process all photos in an album and stream a ZIP archive.

### Request

```
POST /api/albums/7/export
Content-Type: application/json
```

```json
{
  "effects": [
    { "type": "vintage", "intensity": 100 }
  ],
  "format": "jpeg"
}
```

**Body fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `effects` | `EffectParam[]` | Yes | Uniform effect chain applied to every photo in the album; 0–5 items |
| `format` | `"jpeg"` \| `"png"` | Yes | Output format for all photos in the archive |

### Responses

**200 OK** — ZIP archive stream

```
Content-Type: application/zip
Content-Disposition: attachment; filename="album-7-export.zip"
Cache-Control: no-store
```

Body: Streaming ZIP archive. Entry names: `{display_order_index}-{original_filename}.{ext}` (e.g., `001-beach.jpg`).

**400 Bad Request** — validation failure

```json
{
  "error": "VALIDATION_ERROR",
  "message": "effects must have at most 5 items",
  "field": "effects"
}
```

**404 Not Found** — album id does not exist

```json
{ "error": "NOT_FOUND", "message": "Album not found" }
```

**422 Unprocessable Entity** — album exists but has no photos

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Album has no photos to export"
}
```

**500 Internal Server Error** — processing or ZIP failure

```json
{ "error": "INTERNAL_ERROR", "message": "Export failed" }
```

---

## Shared Error Schema

All endpoints reuse the existing `ApiError` type from `src/types/index.ts`:

```typescript
interface ApiError {
  error: 'VALIDATION_ERROR' | 'NOT_FOUND' | 'PAYLOAD_TOO_LARGE' | 'INTERNAL_ERROR';
  message: string;
  field?: string; // present for VALIDATION_ERROR with a specific field
}
```

---

## Effect Type Reference

| `type` | Description | `intensity` effect |
|--------|-------------|-------------------|
| `grayscale` | Remove all color | 0 = original, 100 = full grey |
| `sepia` | Warm brown tone | 0 = original, 100 = full sepia |
| `vintage` | Aged film preset | Ignored (fixed preset) |
| `blur` | Gaussian blur | 0 = no blur, 100 = heavy blur (sigma 8) |
| `sharpen` | Edge enhancement | 0 = subtle, 100 = maximum sharpen |
| `brightness` | Luminance adjust | 0 = darkest (0.5×), 100 = brightest (2.0×) |
| `contrast` | Tonal range | 0 = flattest (0.5×), 100 = highest (2.0×) |
| `saturation` | Color vividness | 0 = desaturated, 100 = maximum saturation (3×) |
