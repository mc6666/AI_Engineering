# UI Contracts: Photo Album Organizer

**Feature**: 001-photo-album-organizer
**Date**: 2026-06-14

These contracts define what each page and component MUST render and what interactions MUST be
available. They are implementation-agnostic at the behavior level; NiceGUI is named only where
the integration pattern requires it (e.g., static mount paths, event binding).

---

## Page Contracts

### Page: Main Page (`/`)

**Purpose**: Entry point showing all albums and the photo import control.

**Preconditions**:
- App is running; SQLite database is initialized.

**Must render**:
- Page title: "Photo Albums"
- Import section: a file-picker control labeled "Import Photos" (accepts multiple files;
  JPEG, PNG, GIF, WEBP)
- Album grid: all albums from the database, ordered by `display_order` ASC
  - If zero albums: empty-state message "No albums yet. Import some photos to get started."
- Each album rendered as an Album Card component (see Component Contracts below)
- Album cards MUST be reorderable via drag-and-drop (SortableJS-backed)

**Must handle**:
- `on_upload(files)`: for each valid image file → Photo Service import → Album Service
  grouping → page refresh
- `on_upload_reject(file)`: display error notification "'{filename}' is not a supported image
  format. Supported formats: JPEG, PNG, GIF, WEBP."
- `on_reorder(ordered_album_ids)`: persist new `display_order` to database; no page refresh
  required (order already reflected in DOM by SortableJS)

**Must NOT render**:
- Implementation internals (file paths, SQL errors, stack traces)
- Navigation chrome beyond a minimal header with the app title

---

### Page: Album Page (`/album/{album_id}`)

**Purpose**: Display all photos in a specific album as a tile grid.

**Preconditions**:
- `album_id` is a valid integer that exists in the database.
- If `album_id` does not exist: redirect to `/` with notification "Album not found."

**Must render**:
- Back navigation control: "← Albums" returning to `/`
- Album label (editable inline; see Interaction below)
- Album date (read-only, shown below the label if label has been customized)
- Photo tile grid: all photos in the album ordered by `date_taken` ASC, then `import_date` ASC
  - If zero photos: message "This album is empty."
- Each photo rendered as a Photo Tile component (see Component Contracts below)
- Lightbox overlay (hidden by default; shown on tile click)

**Must handle**:
- `on_tile_click(photo_id)`: open Lightbox overlay for that photo
- `on_label_edit(new_label)`: persist new album label to database; update header inline
- `on_back()`: navigate to `/`

**Must NOT render**:
- File system paths of photos
- Thumbnail file paths or database IDs exposed to the user

---

## Component Contracts

### Component: Album Card

**Purpose**: Visual representation of one album on the main page.

**Required props**:
- `album_id: int`
- `label: str` — album display name (date string or custom name)
- `cover_thumbnail_url: str | None` — URL of the cover thumbnail; if None, render a
  placeholder icon

**Must render**:
- Drag handle (visible or activated on hover) for SortableJS
- Cover thumbnail image (256×256 px tile, object-fit: cover) or placeholder if None
- Album label below the thumbnail
- `data-album-id` HTML attribute set to `album_id` (required by SortableJS for reorder)

**Must handle**:
- Click on card body (excluding drag handle): navigate to `/album/{album_id}`

---

### Component: Photo Tile

**Purpose**: Thumbnail tile representing one photo inside an album.

**Required props**:
- `photo_id: int`
- `thumbnail_url: str` — URL of the 256×256 thumbnail served from `/thumbnails/`
- `alt_text: str` — filename or date string for accessibility

**Must render**:
- Square thumbnail image (256×256 px, object-fit: cover)
- No visible text overlay on the tile itself

**Must handle**:
- Click: emit `tile_click` event with `photo_id` to parent page

---

### Component: Lightbox

**Purpose**: Enlarged photo overlay displayed when a tile is clicked.

**Required props**:
- `photo_url: str` — URL of the full-resolution image served from `/photos/`
- `alt_text: str`

**Must render**:
- Semi-transparent backdrop covering the full viewport
- Image centered in viewport, constrained to 90% viewport width/height, maintaining aspect ratio
- Close control (× button or click-outside)

**Must handle**:
- Click on backdrop or close control: close overlay, return focus to album tile grid
- Keyboard Escape key: close overlay

---

## Internal API Contracts

These are NiceGUI server-side endpoints used internally (not public REST APIs). They are
documented here for implementation clarity.

### POST `/api/albums/reorder`

**Called by**: SortableJS `onEnd` callback via `ui.run_javascript`

**Request body** (JSON):
```json
{ "ordered_ids": [3, 1, 5, 2, 4] }
```

**Success response**: `200 OK`, body `{ "status": "ok" }`

**Error response**: `422 Unprocessable Entity` if list contains unknown IDs

**Side effect**: Updates `display_order` on each album in the list (position = list index).

---

### GET `/thumbnails/{photo_id}.jpg`

**Served by**: NiceGUI `app.add_media_files('/thumbnails', 'thumbnails/')`

**Returns**: JPEG thumbnail image (256×256 px)

**Error**: 404 if thumbnail not yet generated (triggers on-demand generation)

---

### GET `/photos/{filename}`

**Served by**: NiceGUI `app.add_media_files('/photos', 'photos/')`

**Returns**: Original image file

**Error**: 404 if file not found in photos directory
