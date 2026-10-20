# Quickstart Validation Guide: Photo Album Organizer

**Feature**: Photo Album Organizer
**Date**: 2026-06-15

This guide describes how to set up the project and manually validate each
user story end-to-end. See [contracts/api.md](contracts/api.md) for API
shapes and [data-model.md](data-model.md) for schema details.

---

## Prerequisites

- Node.js 20 LTS (verify: `node --version`)
- npm 10+ (verify: `npm --version`)
- A small folder of sample images on your local machine (JPEG, PNG, or WebP)

---

## Setup

```bash
npm install
npm run db:migrate      # Creates ./data/photo-organizer.db and applies migrations
npm run dev             # Starts Next.js dev server at http://localhost:3000
```

### Environment Variables

All variables have sensible defaults for local development. Override via `.env.local`:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `./data/photo-organizer.db` | Path to the SQLite database file |
| `DATA_DIR` | `./data` | Root for `photos/` and `thumbnails/` subdirectories |
| `MAX_UPLOAD_SIZE_MB` | `20` | Maximum accepted photo file size in megabytes |

---

## Validation Scenario 1 — Browse and Reorder Albums (P1)

**Goal**: Confirm albums display in date-grouped sections and drag-and-drop
reorder persists across page refreshes.

1. Open `http://localhost:3000`
2. **Expected**: Empty state — a message such as "No albums yet" and a "Create Album" call-to-action button
3. Click "Create Album" and fill in:
   - Name: `Summer Road Trip` | Date: `2026-06-01`
   - Confirm / Save
4. Create a second album:
   - Name: `Beach Weekend` | Date: `2026-05-15`
5. **Expected**: Both albums appear on the main page. Each card shows title, date, and a cover thumbnail area. Albums are under their respective month-year headings.
6. Drag `Beach Weekend` above `Summer Road Trip`
7. **Expected**: Album card moves visually during drag; drops into new position on release
8. Refresh the page (`Ctrl+R` / `Cmd+R`)
9. **Expected**: `Beach Weekend` is still listed above `Summer Road Trip` — order persisted
10. Inspect the album list: **Expected**: No album card appears inside another album at any point

**Pass criteria**: All 5 expected outcomes met within 2 s page load.

---

## Validation Scenario 2 — View Photos in an Album (P2)

**Prerequisite**: Complete Scenario 3 first to have an album with photos.

**Goal**: Confirm photo tiles load in grid layout and lightbox navigation works.

1. On the main page, click an album that has at least 5 photos
2. **Expected**: Album view opens. All photos appear as uniform tiles in a grid (consistent tile size, no overflow)
3. **Expected**: Tiles begin appearing without waiting for all to load (progressive rendering)
4. Click any photo tile
5. **Expected**: Full-size photo opens in a lightbox overlay; background content is dimmed
6. Click the next (→) arrow or press the right arrow key
7. **Expected**: Next photo in the album is displayed
8. Click the previous (←) arrow or press the left arrow key
9. **Expected**: Previous photo is displayed
10. Click the close (×) button or press `Escape`
11. **Expected**: Lightbox closes; tile grid is visible and scroll position matches where you left off

**Pass criteria**: All expected outcomes met; album with 5 photos opens in < 3 s.

---

## Validation Scenario 3 — Create Albums and Upload Photos (P3)

**Goal**: Confirm album creation, photo addition, validation, and deletion flows.

### 3a — Create album and add photos

1. Click "Create Album"
2. Enter name: `Birthday Party 2026`, date: `2026-06-10` → Create
3. **Expected**: Album appears on main page under the June 2026 heading
4. Open the album
5. **Expected**: Empty state — message prompting you to add photos
6. Click "Add Photos" and select 3 image files (one JPEG, one PNG, one WebP)
7. **Expected**: Progress indicator (spinner or progress bar) appears during thumbnail generation
8. **Expected**: After processing, 3 photo tiles appear in the grid
9. **Expected**: Main page now shows a cover thumbnail on the album card

### 3b — File validation

10. Click "Add Photos" again and select a non-image file (e.g., a `.pdf` or `.txt` file)
11. **Expected**: An error message appears — "File type not supported" or similar; no new tile is added

### 3c — Delete a photo

12. Hover over or focus a photo tile; click its remove/delete button
13. **Expected**: A confirmation dialog appears ("Are you sure you want to remove this photo?")
14. Confirm deletion
15. **Expected**: The tile disappears; remaining tiles reflow to fill the gap

### 3d — Delete an album

16. Return to the main page
17. Click the delete (trash) icon or button on the `Birthday Party 2026` album card
18. **Expected**: Confirmation dialog appears
19. Confirm deletion
20. **Expected**: Album is removed from the main page immediately

**Pass criteria**: All expected outcomes met for each sub-scenario.

---

## Running Automated Tests

```bash
# Unit tests (album-service, photo-service, file-validation)
npm run test:unit

# Integration tests (API routes against real test.db)
npm run test:integration

# E2E browser tests (requires dev server running in another terminal)
npm run test:e2e

# All Jest tests with line coverage report (must be ≥ 80%)
npm run test:coverage

# Thumbnail generation throughput benchmark (must print ≥ 100 thumbnails/s)
npm run bench:thumbnails
```

---

## Performance Spot Checks

Run these checks to verify constitution Principle IV thresholds:

| Scenario | Playwright test | Pass Threshold |
|----------|----------------|----------------|
| Main page with 100 albums | `album-browse.spec.ts` (seeds 100 albums) | Page idle < 2 s |
| Album with 500 photos | `photo-view.spec.ts` (seeds 500 photos) | Tiles visible < 3 s |
| Drag-and-drop + persist | `album-reorder.spec.ts` | Round-trip < 1 s |
| Thumbnail batch | `npm run bench:thumbnails` | ≥ 100 thumbnails/s |

Playwright specs seed and clean up their own test data via the API — no
manual database setup required.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `better-sqlite3` import error on start | Native addon not built for current Node version | `npm rebuild better-sqlite3` |
| HEIC files rejected | `libheif` not bundled on this platform | Install `heic-convert`: `npm install heic-convert` |
| Thumbnails not generating | `sharp` native binding mismatch | `npm rebuild sharp` |
| DB file not found | Migration not run | `npm run db:migrate` |
