# Tasks: Image Processing with Special Effects & Export

**Input**: Design documents from `specs/002-image-effects-export/`

**Prerequisites**: plan.md ✅ spec.md ✅ research.md ✅ data-model.md ✅ contracts/api.md ✅ quickstart.md ✅

**Tests**: Included — project constitution (`.specify/memory/constitution.md` Principle II) mandates TDD for all new feature work. Tests MUST be written first, confirmed to fail, then implemented.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no in-phase dependencies)
- **[Story]**: Which user story (US1, US2, US3)
- Exact file paths are included in every task description

## Path Conventions

Single Next.js monolith (established in spec 001 plan.md):
- Source: `src/` at repository root
- Tests: `tests/unit/`, `tests/integration/`, `tests/e2e/` at repository root
- Scripts: `scripts/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add the one new dependency and extend shared types before any user-story work begins.

- [x] T001 Install archiver ^7 and @types/archiver ^5 by running `npm install archiver` and `npm install -D @types/archiver` and committing updated package.json and package-lock.json
- [x] T002 [P] Extend `src/types/index.ts` with `EffectType`, `EffectParam`, `EffectChain`, `OutputFormat`, `ProcessRequest`, and `ExportRequest` as specified in data-model.md
- [x] T003 [P] Create `scripts/bench-effects.ts` — performance benchmark that processes 100 fixture images through each effect type via `effect-service`, prints per-effect throughput in photos/s; must follow the same pattern as `scripts/bench-thumbnails.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: `effect-service.ts` is the shared processing core required by all three user stories. It must be complete and tested before any API route or UI component is built.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

### Tests for Foundational Phase ⚠️

> **Write these tests FIRST — they MUST FAIL before T005 is written (TDD Red phase)**

- [x] T004 Write failing unit tests for `effect-service` in `tests/unit/services/effect-service.test.ts` — one test per effect type (grayscale, sepia, vintage, blur, sharpen, brightness, contrast, saturation) each using a real fixture image; one test for chain-of-5; one test for empty chain (output equals input format); one test that a chain > 5 items throws; use `tests/fixtures/images/sample.jpg` and `tests/fixtures/images/sample.png` as inputs, never mock `sharp`

### Implementation for Foundational Phase

- [x] T005 Implement `src/lib/services/effect-service.ts` — export `applyEffects(buffer: Buffer, chain: EffectChain, format: OutputFormat): Promise<Buffer>` using `sharp`; map each `EffectType` to the sharp operations from data-model.md Effect-to-Sharp Pipeline Rules; validate chain length ≤ 5 and throw on unknown type; encode output per `OutputFormat` rules (jpeg quality 90 progressive, png compressionLevel 6)

**Checkpoint**: Run `npm run test:unit -- --testPathPattern="effect-service"` — all tests green. Foundation ready; user story phases can now proceed.

---

## Phase 3: User Story 1 — Apply Special Effects to a Photo (Priority: P1) 🎯 MVP

**Goal**: Users open an effects panel on any photo in the lightbox, select one of 8 effects, adjust intensity with a slider, see a live CSS filter preview, and click Reset to clear all effects. No server calls are needed for preview.

**Independent Test**: Open a photo in the lightbox, click "Effects", click Grayscale tile, verify the preview goes greyscale within 500 ms, drag slider to 50 and verify partial greyscale, click Reset and verify color is restored.

### Tests for User Story 1 ⚠️

> **Write these tests FIRST — they MUST FAIL before T007–T009 are written (TDD Red phase)**

- [x] T006 [P] [US1] Write failing E2E test for effects panel in `tests/e2e/photo-effects.spec.ts` — scenarios: (1) open lightbox → click Effects button → panel renders with 8 effect tiles; (2) click Grayscale tile → preview has CSS `filter: grayscale(1)` applied within 500 ms; (3) move intensity slider to 50 → filter updates to `grayscale(0.5)`; (4) click Reset → filter returns to `none`; use `page.locator` and `toHaveCSS` assertions; run axe-core accessibility audit on the open panel

### Implementation for User Story 1

- [x] T007 [P] [US1] Create `src/components/EffectPreview.tsx` — wraps `<img>` with a dynamically computed `style.filter` CSS string; export a pure helper `deriveCssFilter(chain: EffectChain): string` that maps each `EffectParam` to the CSS token from research.md Decision 1 table; returns `'none'` for empty chain
- [x] T008 [P] [US1] Create `src/components/EffectsPanel.tsx` — renders 8 effect tiles (name + icon/swatch), an intensity slider (`<input type="range" min={0} max={100}>`), and a Reset button; manages selected effect and per-effect intensity in local state; calls `onChainChange(chain: EffectChain)` callback on every change; all tiles and slider carry ARIA labels; keyboard-accessible (Tab focus, Enter to select)
- [x] T009 [US1] Update `src/components/LightboxOverlay.tsx` — add an "Effects" toggle button in the toolbar; when open, render `EffectsPanel` and replace the main `<img>` with `EffectPreview`; manage `effectChain: EffectChain` state (initially `[]`); pass `onChainChange` to `EffectsPanel` and `chain` to `EffectPreview`

**Checkpoint**: Run `npx playwright test e2e/photo-effects.spec.ts` — US1 tests green. Open a photo → click Effects → select Grayscale → preview renders grey → Reset restores color. User Story 1 is independently testable.

---

## Phase 4: User Story 2 — Download a Single Processed Photo (Priority: P2)

**Goal**: A user with an effect chain applied clicks "Download" in the effects panel, selects JPEG or PNG, and the processed photo is saved to their device.

**Independent Test**: Apply Sepia at intensity 80, select JPEG, click Download, verify the browser saves `photo-{id}-processed.jpg` and the file is a warm sepia-toned JPEG.

### Tests for User Story 2 ⚠️

> **Write these tests FIRST — they MUST FAIL before T011 is written (TDD Red phase)**

- [x] T010 [P] [US2] Write failing integration tests for the process route in `tests/integration/api/process.test.ts` — scenarios: (1) POST with valid effect chain + format returns 200, `Content-Type: image/jpeg`, `Content-Disposition: attachment`; (2) empty chain returns the original image in the requested format; (3) effects chain > 5 items returns 400 VALIDATION_ERROR; (4) unknown effect type returns 400; (5) non-existent photo ID returns 404; use Supertest against the real SQLite test DB and `tests/fixtures/images/sample.jpg` as the source photo; never mock `sharp` or the filesystem

### Implementation for User Story 2

- [x] T011 [US2] Create `src/app/api/photos/[id]/process/route.ts` — parse `ProcessRequest` from request JSON body; validate chain length, effect types, intensity range, and format; look up photo filepath from DB via `getImagePath()`; read source file buffer; call `effect-service.applyEffects()`; return binary result as `Response` with `Content-Type`, `Content-Disposition: attachment; filename="photo-{id}-processed.{ext}"`, and `Cache-Control: no-store`; return typed `ApiError` JSON for all validation and 404 cases
- [x] T012 [US2] Add a format selector dropdown (`jpeg` / `png`) and a "Download" button to `src/components/EffectsPanel.tsx` — on click, POST current `effectChain` + selected format to `/api/photos/${photoId}/process` using `fetch` with an `AbortController`; create a Blob URL and trigger `<a download>` click; show a loading spinner during the request; expose a cancel mechanism that calls `controller.abort()`

**Checkpoint**: Run `npm run test:integration -- --testPathPattern="process"` — tests green. In the running app, apply Sepia, click Download → browser saves a sepia JPEG. User Story 2 is independently testable.

---

## Phase 5: User Story 3 — Batch Export Photos or Albums (Priority: P3)

**Goal**: Users select multiple photos or an entire album, apply a uniform effect, and export a ZIP archive with progress feedback and cancel support.

**Independent Test**: Navigate to an album with 5+ photos, click "Export Album", select Vintage + JPEG, watch progress count, verify a ZIP is downloaded containing one JPEG per album photo with vintage treatment applied.

### Tests for User Story 3 ⚠️

> **Write these tests FIRST — they MUST FAIL before T014–T016 are written (TDD Red phase)**

- [x] T013 [US3] Write failing integration tests for batch export routes in `tests/integration/api/export.test.ts` — scenarios for `/api/photos/export`: (1) valid photoIds + effects returns 200, `Content-Type: application/zip`, ZIP contains one entry per photoId; (2) empty `photoIds` returns 400; (3) one or more IDs not found returns 404; (4) empty effects chain returns ZIP with original-format images. Scenarios for `/api/albums/[id]/export`: (5) valid album returns 200 ZIP with all album photos; (6) non-existent album returns 404; (7) album with no photos returns 422. Use Supertest + real DB + real fixture images; verify ZIP entry count and that each entry is a valid image buffer

### Implementation for User Story 3

- [x] T014 [US3] Create `src/lib/services/export-service.ts` — export `buildZipStream(photos: Array<{id: number, filepath: string, filename: string}>, chain: EffectChain, format: OutputFormat, dataDir?: string): Readable` — for each photo: read source buffer, call `effect-service.applyEffects()`, append result to an `archiver('zip')` instance; entry name pattern `{index:03d}-{filename}.{ext}`; finalize and return the archiver stream; process photos sequentially to keep memory flat
- [x] T015 [P] [US3] Create `src/app/api/photos/export/route.ts` — parse `ExportRequest` body (validate `photoIds` non-empty, effects chain, format); look up each photo from DB via `getPhotoById()`; collect 404s and return early if any missing; call `export-service.buildZipStream()`; return streaming `Response` with `Content-Type: application/zip`, `Content-Disposition: attachment; filename="photos-export.zip"`, `Cache-Control: no-store`
- [x] T016 [P] [US3] Create `src/app/api/albums/[id]/export/route.ts` — look up album by id; return 404 if not found; query all photos for that album ordered by `display_order`; return 422 if album has no photos; call `export-service.buildZipStream()`; return streaming `Response` with `Content-Disposition: attachment; filename="album-{id}-export.zip"`
- [x] T017 [US3] Create `src/components/ExportDialog.tsx` — modal dialog with: scope tabs ("Selected Photos" / "Album"); format selector (jpeg/png); uniform effect picker (same 8 tiles as EffectsPanel, single-select); intensity slider; Export button; progress counter (`{n} / {total} photos processed`); Cancel button that calls `controller.abort()`; on export: POST to the appropriate route, stream response into a Blob, trigger `<a download>` when complete; show error toast on failure; ARIA role="dialog", focus-trapped, keyboard-closeable
- [x] T018 [US3] Update `src/app/albums/[id]/page.tsx` — add photo multi-select mode toggle; checkboxes on each `PhotoTile` when mode is active; "Export Selected" button (disabled when selection empty) and "Export Album" button in toolbar; clicking either opens `ExportDialog` with the appropriate scope; pass `albumId` and `selectedPhotoIds` as props

**Checkpoint**: Run `npm run test:integration -- --testPathPattern="export"` — tests green. In the running app: export a 5-photo album with Vintage effect → progress shows 1/5…5/5 → browser downloads a ZIP with 5 JPEG files. User Story 3 is independently testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Performance gate, full E2E verification, coverage gate, and quickstart validation.

- [x] T019 [P] Run `npx ts-node --project tsconfig.scripts.json scripts/bench-effects.ts` and confirm output shows ≥ 10 photos/s for every effect type; fix any effect pipeline that falls below threshold
- [x] T020 [P] Run `npx playwright test e2e/photo-effects.spec.ts` — verify all 6 quickstart.md scenarios pass including the axe-core accessibility audit on the effects panel and export dialog
- [x] T021 [P] Run `npm run test:coverage` — verify overall line coverage ≥ 80%; if coverage drops, add targeted unit tests for any uncovered branches in `effect-service.ts` or `export-service.ts`
- [x] T022 [P] Run full test suite `npm run test:unit && npm run test:integration` — confirm zero regressions in spec 001 tests (album-service, photo-service, file-validation, albums API, photos API)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately; T002 and T003 can run in parallel with T001 after archiver types are known
- **Foundational (Phase 2)**: Depends on Setup (T001, T002 must be complete); T004 written before T005; **BLOCKS all user story phases**
- **User Story Phases (3–5)**: All depend on Foundational completion (T004, T005 must pass)
  - Phase 3 (US1): No dependency on US2 or US3
  - Phase 4 (US2): Depends on Phase 3 completion (EffectsPanel must exist to add the Download button in T012)
  - Phase 5 (US3): Depends on Phase 3 (EffectsPanel tile pattern reused in ExportDialog T017); T015 and T016 can run in parallel once T014 is complete
- **Polish (Phase 6)**: Depends on all desired user story phases complete; all polish tasks run in parallel

### User Story Dependencies

- **US1 (P1)**: After Foundational — independent
- **US2 (P2)**: After US1 (T012 adds Download button to EffectsPanel created in T008)
- **US3 (P3)**: After US1 (T017 ExportDialog reuses effect tile pattern from T008); T015 and T016 independent of each other after T014

### Within Each User Story

- TDD: Write test → confirm RED → implement → confirm GREEN
- Models and types before services; services before routes; routes before UI integration
- Each story MUST be independently demoed at its checkpoint before proceeding

### Parallel Opportunities

| When | Parallel tasks |
|------|---------------|
| Phase 1 | T002, T003 (after T001 completes) |
| Phase 3 | T006, T007, T008 (different files; T009 depends on T007+T008) |
| Phase 4 | T010 can be written while T009 is in progress |
| Phase 5 | T015, T016 (different route files; both depend on T014) |
| Phase 6 | T019, T020, T021, T022 (all independent) |

---

## Parallel Example: User Story 1

```bash
# Write E2E test, EffectsPanel, and EffectPreview concurrently (all different files):
Task: T006 — tests/e2e/photo-effects.spec.ts
Task: T007 — src/components/EffectPreview.tsx
Task: T008 — src/components/EffectsPanel.tsx

# Then (depends on T007 + T008):
Task: T009 — src/components/LightboxOverlay.tsx (integration)
```

## Parallel Example: User Story 3 (after T014 complete)

```bash
# Both routes are independent files:
Task: T015 — src/app/api/photos/export/route.ts
Task: T016 — src/app/api/albums/[id]/export/route.ts
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T003)
2. Complete Phase 2: Foundational (T004–T005) — **blocks all stories**
3. Complete Phase 3: User Story 1 (T006–T009)
4. **STOP and VALIDATE**: Effects panel previews work in lightbox; E2E green
5. Demo: live CSS filter preview on any photo — no download needed yet

### Incremental Delivery

1. Setup + Foundational → effect-service tested and green
2. US1 → Effects panel in lightbox with live preview (MVP!)
3. US2 → Download button + process API route → single photo download works
4. US3 → Batch export service + routes + ExportDialog → full album ZIP export
5. Polish → all gates pass; full test suite green

### Single-Developer Sequence

```
T001 → T002, T003 [parallel]
→ T004 → T005
→ T006, T007, T008 [parallel] → T009
→ T010 → T011 → T012
→ T013 → T014 → T015, T016 [parallel] → T017 → T018
→ T019, T020, T021, T022 [parallel]
```

---

## Notes

- `[P]` tasks operate on different files and have no in-phase dependencies
- `[US#]` label maps every task to the user story it delivers, for traceability
- TDD is mandatory per constitution Principle II — never implement before the test is written and red
- Never mock `sharp`, the filesystem, or SQLite in integration tests (constitution Principle II)
- Each phase checkpoint must be verified before proceeding
- Commit after each task or logical group; no "big bang" commits (constitution Development Workflow)
- The `main` branch must remain deployable at all times — use the `002-image-effects-export` branch
