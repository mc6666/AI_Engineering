# Quickstart & Validation Guide: Image Effects & Export

**Feature**: Image Processing with Special Effects & Export
**Date**: 2026-06-17

This guide covers how to validate the feature end-to-end once implementation is complete. It is not a tutorial and does not include implementation code.

---

## Prerequisites

- Node.js 20 LTS
- `npm install` run at the project root (installs `archiver` and `@types/archiver` in addition to existing deps)
- Database migrated: `npm run db:migrate`
- Development server running: `npm run dev`
- At least one album with 3+ photos already in the organizer

---

## Scenario 1: Live Effect Preview

**What to verify**: Selecting an effect applies a visible CSS filter to the photo preview within 500 ms — no server call involved.

1. Open the application at `http://localhost:3000`
2. Click into any album that has photos
3. Click a photo tile to open the lightbox
4. Click the "Effects" button (or panel trigger) to open the Effects panel
5. Click the **Grayscale** effect tile

**Expected**: The photo preview renders in greyscale within 500 ms.

6. Drag the intensity slider to 50

**Expected**: The preview updates to approximately 50% greyscale in real time.

7. Click **Reset**

**Expected**: Preview returns to the original color photo; all effects cleared.

---

## Scenario 2: Single Photo Download

**What to verify**: Applying an effect and clicking "Download" saves a processed file to disk with the effect applied.

1. Open a photo in the effects panel (Scenario 1, steps 1–4)
2. Select the **Sepia** effect and set intensity to 80
3. Select **JPEG** from the format dropdown
4. Click **Download**

**Expected**:
- Browser download dialog appears (or file saves automatically to Downloads folder)
- Saved filename matches pattern `photo-{id}-processed.jpg`
- Opening the file shows a warm sepia-toned image
- The original photo in the organizer is unchanged

---

## Scenario 3: Batch Export — Photo Selection

**What to verify**: Multi-selecting photos and exporting downloads a ZIP with all photos processed.

1. On an album page, select 3–5 photos using the multi-select mechanism (checkbox or Ctrl+click)
2. Click **Export Selected**
3. In the Export dialog, select **Blur** at intensity 20 and **PNG** format
4. Click **Export**

**Expected**:
- A progress indicator appears while the ZIP is being generated
- Browser downloads a file named `photos-export.zip`
- Opening the ZIP shows one `.png` file per selected photo
- Each image in the ZIP has a visible blur applied
- Original photos in the organizer are unchanged

---

## Scenario 4: Batch Export — Full Album

**What to verify**: Exporting a full album downloads a ZIP of all photos in the album.

1. Navigate to an album view with at least 5 photos
2. Click **Export Album**
3. Select **Vintage** effect and **JPEG** format in the dialog
4. Click **Export**

**Expected**:
- Progress indicator shows `N / total` count as photos are processed
- Browser downloads `album-{id}-export.zip`
- ZIP contains one `.jpg` per photo in the album, in display order
- Each image shows the vintage color treatment
- No original photos are modified

---

## Scenario 5: Export Cancellation

**What to verify**: Cancelling a batch export stops it cleanly with no partial files.

1. Start an Export Album operation on an album with 20+ photos
2. Click **Cancel** while the progress indicator is active (before it reaches 100%)

**Expected**:
- Download dialog does not appear
- No file is saved to disk
- The organizer returns to normal state within 2 seconds
- Original photos are unchanged

---

## Scenario 6: Validation Errors

**What to verify**: The API rejects invalid requests with clear error messages.

Using curl or a REST client:

```bash
# Too many effects (> 5)
curl -X POST http://localhost:3000/api/photos/1/process \
  -H "Content-Type: application/json" \
  -d '{"effects":[{"type":"blur","intensity":10},{"type":"blur","intensity":20},{"type":"blur","intensity":30},{"type":"blur","intensity":40},{"type":"blur","intensity":50},{"type":"blur","intensity":60}],"format":"jpeg"}'
```

**Expected**: `400 Bad Request` with `{ "error": "VALIDATION_ERROR", "message": "effects must have at most 5 items" }`

```bash
# Unknown effect type
curl -X POST http://localhost:3000/api/photos/1/process \
  -H "Content-Type: application/json" \
  -d '{"effects":[{"type":"oil_paint","intensity":50}],"format":"jpeg"}'
```

**Expected**: `400 Bad Request` with `{ "error": "VALIDATION_ERROR", "message": "Unknown effect type: oil_paint" }`

```bash
# Empty album export
curl -X POST http://localhost:3000/api/albums/999/export \
  -H "Content-Type: application/json" \
  -d '{"effects":[],"format":"jpeg"}'
```

**Expected**: `404 Not Found` (if album 999 does not exist)

---

## Automated Test Commands

```bash
# Run unit tests for effect-service
npm run test:unit -- --testPathPattern="effect-service"

# Run integration tests for new routes
npm run test:integration -- --testPathPattern="process|export"

# Run E2E effects flow
npx playwright test e2e/photo-effects.spec.ts

# Run effect pipeline benchmark
npx ts-node --project tsconfig.scripts.json scripts/bench-effects.ts
# Expected output: ≥ 10 photos/s for each effect type

# Full test suite with coverage
npm run test:coverage
# Coverage must remain ≥ 80%
```

---

## Cross-references

- Effect type definitions → [data-model.md](../data-model.md)
- API request/response contracts → [contracts/api.md](../contracts/api.md)
- Sharp pipeline mapping → [research.md](../research.md) Decision 2
- CSS filter preview mapping → [research.md](../research.md) Decision 1
