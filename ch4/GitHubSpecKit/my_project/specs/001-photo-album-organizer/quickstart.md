# Quickstart Validation Guide: Photo Album Organizer

**Feature**: 001-photo-album-organizer
**Date**: 2026-06-14

This guide provides end-to-end validation scenarios that prove the feature works correctly.
Run these scenarios after completing the implementation to confirm all user stories are functional.

---

## Prerequisites

- Python 3.11+ installed
- Dependencies installed: `pip install nicegui pillow aiosqlite`
- Working directory: repository root
- Sample image files available (JPEG/PNG with EXIF data; see test fixtures in `tests/fixtures/`)

---

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start the application
python src/main.py
```

Expected: NiceGUI prints a local URL (e.g., `http://localhost:8080`) and opens the default
browser automatically. The main page loads with an empty-state message.

---

## Validation Scenarios

### Scenario 1: Empty State (US2)

**Steps**:
1. Open the app for the first time (no imports done).
2. Observe the main page.

**Expected**:
- Page title "Photo Albums" is visible.
- Empty-state message appears: "No albums yet. Import some photos to get started."
- No album cards are shown.
- Import control is visible.

---

### Scenario 2: Import Photos — Single Date (US1)

**Steps**:
1. Prepare 3 JPEG images all with EXIF date `2024-06-15`.
2. Click "Import Photos" and select all 3 files.
3. Wait for import to complete.
4. Observe the main page.

**Expected**:
- One album card appears labeled `2024-06-15`.
- Album card shows a cover thumbnail from one of the imported photos.
- No error messages.

**Verify in database** (optional, for debugging):
```bash
sqlite3 data/photo_organizer.db "SELECT id, label, date FROM albums;"
sqlite3 data/photo_organizer.db "SELECT id, filename, album_id FROM photos;"
```

---

### Scenario 3: Import Photos — Multiple Dates (US1, SC-001)

**Steps**:
1. Prepare 20 JPEG images spanning 3 different dates (e.g., 7 from `2024-07-01`,
   8 from `2024-07-02`, 5 from `2024-07-03`).
2. Click "Import Photos" and select all 20 files simultaneously.
3. Time the operation.
4. Observe the main page.

**Expected**:
- Import completes within 30 seconds (SC-001).
- Exactly 3 album cards appear, one per date.
- Each album card shows the correct date label.
- Photo counts per album match (7, 8, and 5 photos respectively).

---

### Scenario 4: Duplicate Date Protection (FR-003)

**Steps**:
1. Import 2 photos with EXIF date `2024-08-10` (one album is created).
2. Import 1 more photo with EXIF date `2024-08-10`.
3. Observe the main page.

**Expected**:
- Still exactly one album for `2024-08-10`.
- The album now contains 3 photos total.

---

### Scenario 5: Non-Image File Rejection (FR-009, SC-007)

**Steps**:
1. Attempt to import a PDF file or text file.
2. Observe the result.

**Expected**:
- Upload is rejected; no album is created or modified.
- Error notification appears: "'{filename}' is not a supported image format.
  Supported formats: JPEG, PNG, GIF, WEBP."

---

### Scenario 6: No EXIF Date Fallback (FR-002)

**Steps**:
1. Import a PNG file with no EXIF metadata (e.g., a screenshot).
2. Observe the result.

**Expected**:
- Photo is placed in an album for today's date.
- An informational notification appears indicating the upload date was used.

---

### Scenario 7: View Album Tile Grid (US4, SC-004)

**Steps**:
1. Import at least 10 photos.
2. Click on an album card.
3. Time how long the tile grid takes to fully render.
4. Confirm the album page URL changes to `/album/{id}`.

**Expected**:
- All photo tiles appear within 3 seconds (SC-004, up to 100 photos).
- All tiles are equal-size squares.
- Back navigation control "← Albums" is visible.
- Album label is shown at the top.

---

### Scenario 8: Lightbox Photo Preview (US4, FR-008)

**Steps**:
1. Open an album page with at least one photo.
2. Click a photo tile.
3. Observe the overlay.
4. Press Escape or click outside the image.

**Expected**:
- A darkened overlay appears with the full-resolution photo centered.
- Photo maintains its aspect ratio.
- Pressing Escape or clicking the backdrop closes the overlay.
- After close, the tile grid is visible and responsive.

---

### Scenario 9: Album Rename (FR-011)

**Steps**:
1. Open an album page.
2. Click the album label to edit it.
3. Change the label to "Summer Vacation".
4. Confirm (Enter or click away).
5. Navigate back to the main page.

**Expected**:
- The album card on the main page shows "Summer Vacation" instead of the date.
- The date is still visible below the custom label on the album page.
- After a page refresh, the custom label persists.

---

### Scenario 10: Drag-and-Drop Reorder and Persistence (US3, SC-003, SC-006)

**Steps**:
1. Ensure at least 3 albums exist.
2. Drag the last album card to the first position and release.
3. Note the new order: album that was last is now first.
4. Refresh the browser page.
5. Observe the album order.

**Expected**:
- Visual reorder completes within 300 ms of drag start (SC-003).
- Order is saved within 1 second of drop (SC-003).
- After page refresh, the custom order is preserved exactly (SC-006).

---

### Scenario 11: Main Page Performance (SC-002)

**Steps**:
1. Import enough photos to create 50 albums (one photo per unique date, 50 dates).
2. Navigate to the main page.
3. Time the page load.

**Expected**:
- Main page fully renders within 3 seconds (SC-002).
- All 50 album cards are visible (may require scrolling).

---

## Teardown / Reset

To reset the app to a clean state for re-testing:

```bash
# Stop the app (Ctrl+C in terminal)
# Remove database and thumbnails
rm data/photo_organizer.db
rm -rf thumbnails/
rm -rf photos/
# Restart
python src/main.py
```

---

## References

- Data model and schema: [data-model.md](data-model.md)
- UI contracts and page specs: [contracts/ui-contracts.md](contracts/ui-contracts.md)
- Technology decisions: [research.md](research.md)
- Feature requirements: [spec.md](spec.md)
