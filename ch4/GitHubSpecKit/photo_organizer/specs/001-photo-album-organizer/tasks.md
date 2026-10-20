---

description: "Task list for Photo Album Organizer implementation"
---

# Tasks: Photo Album Organizer

**Input**: Design documents from `/specs/001-photo-album-organizer/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/api.md ✅

**Tests**: Included — constitution mandates TDD (Red → Green → Refactor). Test tasks
MUST be completed and confirmed failing before each corresponding implementation task.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description with file path`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[Story]**: Maps to user story from spec.md ([US1], [US2], [US3])
- Every task includes an exact file path

## Path Conventions

- Next.js monolith at repository root
- `src/app/` — App Router pages and API routes
- `src/components/` — React components
- `src/lib/` — DB schema, services, validation
- `src/types/` — Shared TypeScript interfaces
- `tests/` — unit/, integration/, e2e/, fixtures/
- `data/` — runtime data (gitignored; created by db:migrate)

---

## Phase 1: Setup

**Purpose**: Project initialization and tooling configuration

- [X] T001 Initialize Next.js 15 project with TypeScript, App Router, and Tailwind CSS v4 in package.json, tsconfig.json, and next.config.ts
- [X] T002 Install core npm dependencies: better-sqlite3, drizzle-orm, drizzle-kit, @dnd-kit/core, @dnd-kit/sortable, sharp, @types/better-sqlite3
- [X] T003 [P] Configure Jest 29 + ts-jest for unit and integration tests in jest.config.ts and jest.setup.ts
- [X] T004 [P] Configure Playwright in playwright.config.ts with chromium target, baseURL http://localhost:3000, and webServer block
- [X] T005 [P] Configure ESLint with eslint-plugin-sonarjs in eslint.config.mjs enforcing cyclomatic complexity ≤ 10 per function
- [X] T006 [P] Create tests/fixtures/images/ with committed sample files: sample.jpg, sample.png, sample.webp, sample.gif, invalid.pdf

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database schema, connection, shared types, layout — MUST complete before any user story work

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete

- [X] T007 Define Drizzle ORM schema for albums and photos tables (per data-model.md) in src/lib/db/schema.ts
- [X] T008 Configure Drizzle Kit in drizzle.config.ts and run `npx drizzle-kit generate` to produce initial migration SQL in src/lib/db/migrations/
- [X] T009 Implement better-sqlite3 singleton connection with auto-migration runner (applies all pending migrations on import) in src/lib/db/client.ts
- [X] T010 [P] Define shared TypeScript interfaces Album, Photo, and ApiError (per contracts/api.md shapes) in src/types/index.ts
- [X] T011 [P] Create Tailwind CSS global styles in src/app/globals.css and root layout with metadata in src/app/layout.tsx
- [X] T012 [P] Add all npm scripts to package.json: dev, build, db:migrate, test:unit, test:integration, test:e2e, test:coverage, bench:thumbnails
- [X] T013 [P] Write unit tests for AlbumService.getAll() and getById() — confirm tests fail before T014 in tests/unit/services/album-service.test.ts
- [X] T014 Implement AlbumService.getAll() (albums with photoCount and coverThumbnailUrl) and getById() (album + ordered photos array) in src/lib/services/album-service.ts

**Checkpoint**: DB connects, schema migrated, core service reads tested and working. User story phases can now begin.

---

## Phase 3: User Story 1 — Browse and Reorder Albums (Priority: P1) 🎯 MVP

**Goal**: Main page shows all albums in date-grouped sections. Drag-and-drop reorders albums and the new order persists across page refreshes. Flat hierarchy enforced — no album nests inside another.

**Independent Test**: Seed two albums directly into SQLite (via db helper), load `http://localhost:3000`, verify date headings, drag one album past the other, refresh, confirm order persisted.

### Tests for User Story 1 ⚠️ Write BEFORE implementation and confirm they fail

- [X] T015 [P] [US1] Write unit tests for AlbumService.reorder(): mid-point, move-to-start, move-to-end, renormalization trigger (gap < 0.001) in tests/unit/services/album-service.test.ts
- [X] T016 [P] [US1] Write integration tests for GET /api/albums (returns ordered albums) and POST /api/albums/[id]/reorder (updates display_order) against real test.db in tests/integration/api/albums.test.ts

### Implementation for User Story 1

- [X] T017 [US1] Implement AlbumService.reorder() with fractional-index calculation and full-list renormalization when gap < 0.001 in src/lib/services/album-service.ts
- [X] T018 [US1] Implement GET /api/albums route handler returning albums ordered by display_order in src/app/api/albums/route.ts
- [X] T019 [US1] Implement POST /api/albums/[id]/reorder route handler computing new display_order from predecessorOrder and successorOrder fields in src/app/api/albums/[id]/reorder/route.ts
- [X] T020 [P] [US1] Implement AlbumCard component showing album title, date badge, cover thumbnail (or placeholder), and photo count in src/components/AlbumCard.tsx
- [X] T021 [P] [US1] Implement EmptyState component with message text and optional call-to-action slot in src/components/EmptyState.tsx
- [X] T022 [US1] Implement AlbumGrid component wrapping @dnd-kit/sortable DndContext and SortableContext; on drag end, call POST reorder API and apply optimistic order update in src/components/AlbumGrid.tsx
- [X] T023 [US1] Implement main page: fetch albums via GET /api/albums, group by year-month, render date section headings and AlbumGrid (or EmptyState if no albums) in src/app/page.tsx
- [X] T024 [US1] Write Playwright E2E tests: empty state renders → seed 2 albums via API → date headings appear → drag-and-drop → page refresh → order persisted in tests/e2e/album-browse.spec.ts and tests/e2e/album-reorder.spec.ts

**Checkpoint**: User Story 1 fully functional and independently testable. Main page shows date-grouped albums with working persistent drag-and-drop.

---

## Phase 4: User Story 2 — View Photos in an Album (Priority: P2)

**Goal**: Clicking an album opens a tile grid of all its photos. Clicking a tile opens a full-size lightbox with previous/next navigation and keyboard support. Tiles load progressively.

**Independent Test**: Seed one album with 5 photos via the API (using image fixtures), navigate to the album URL, verify tile grid renders, click a tile, verify lightbox opens, navigate forward/backward, press Escape, verify scroll position is restored.

### Tests for User Story 2 ⚠️ Write BEFORE implementation and confirm they fail

- [X] T025 [P] [US2] Write unit tests for PhotoService read methods: getByAlbumId(), getImagePath() (path traversal guard), getThumbnailPath() in tests/unit/services/photo-service.test.ts
- [X] T026 [P] [US2] Write integration tests for GET /api/albums/[id] (returns album + photos), GET /api/photos/[id]/image (streams bytes), GET /api/photos/[id]/thumbnail (streams JPEG) against real test.db with sample.jpg fixture in tests/integration/api/albums.test.ts and tests/integration/api/photos.test.ts

### Implementation for User Story 2

- [X] T027 [US2] Implement PhotoService.getByAlbumId(), getImagePath(), and getThumbnailPath() with DATA_DIR resolution and path-traversal guard (`path.resolve` must start with DATA_DIR) in src/lib/services/photo-service.ts
- [X] T028 [US2] Implement GET /api/albums/[id] route handler returning album object plus ordered photos array in src/app/api/albums/[id]/route.ts
- [X] T029 [US2] Implement GET /api/photos/[id]/image streaming route: resolve file path via PhotoService, stream via ReadableStream, set Content-Type from mime_type and Cache-Control: public, max-age=31536000, immutable in src/app/api/photos/[id]/image/route.ts
- [X] T030 [US2] Implement GET /api/photos/[id]/thumbnail streaming route: stream thumbnail JPEG with Content-Type: image/jpeg and immutable cache headers in src/app/api/photos/[id]/thumbnail/route.ts
- [X] T031 [P] [US2] Implement PhotoTile component: renders thumbnail URL in an <img> with loading="lazy", fixed tile dimensions, and onClick handler in src/components/PhotoTile.tsx
- [X] T032 [US2] Implement PhotoGrid component: CSS grid layout with responsive columns, renders PhotoTile for each photo, passes selected index to parent in src/components/PhotoGrid.tsx
- [X] T033 [US2] Implement LightboxOverlay component: full-size <img>, previous/next buttons, left/right arrow key listeners, Escape to close, backdrop click to close in src/components/LightboxOverlay.tsx
- [X] T034 [US2] Implement album view page: fetch album + photos via GET /api/albums/[id], render PhotoGrid with LightboxOverlay, restore scroll position on lightbox close in src/app/albums/[id]/page.tsx
- [X] T035 [US2] Write Playwright E2E tests: navigate to album → tile grid loads in < 3 s → click tile → lightbox opens → next/prev buttons work → arrow keys work → Escape closes → scroll position restored in tests/e2e/photo-view.spec.ts

**Checkpoint**: User Stories 1 and 2 both independently functional and testable. Album view shows progressive tile grid and working lightbox.

---

## Phase 5: User Story 3 — Create Albums and Upload Photos (Priority: P3)

**Goal**: Users create named, dated albums via a modal, upload photos (JPEG/PNG/WebP/GIF/HEIC) via file picker with progress feedback, see tiles appear, remove individual photos with confirmation, and delete entire albums with confirmation.

**Independent Test**: Click "Create Album" → fill form → album appears on main page → open album → upload 3 images → tiles appear → attempt invalid file → error shown → delete one photo → tiles reflow → return to main page → delete album → album removed.

### Tests for User Story 3 ⚠️ Write BEFORE implementation and confirm they fail

- [X] T036 [P] [US3] Write unit tests for file-validation.ts: accept JPEG/PNG/WebP/GIF/HEIC by magic bytes, reject PDF/text/executable, reject files exceeding 20 MB in tests/unit/validation/file-validation.test.ts
- [X] T037 [P] [US3] Write unit tests for AlbumService.create(), update(), and delete() (including cover_photo_id cascade clearing) in tests/unit/services/album-service.test.ts
- [X] T038 [P] [US3] Write unit tests for PhotoService.addPhoto() (thumbnail generation with sharp using sample.jpg fixture) and PhotoService.removePhoto() (file cleanup and cover update) in tests/unit/services/photo-service.test.ts
- [X] T039 [US3] Write integration tests for POST /api/albums, PUT /api/albums/[id], DELETE /api/albums/[id], POST /api/albums/[id]/photos (multipart with real image), DELETE /api/photos/[id] in tests/integration/api/albums.test.ts and tests/integration/api/photos.test.ts

### Implementation for User Story 3

- [X] T040 [P] [US3] Implement file-validation.ts: read first 12 bytes, check magic byte signatures for JPEG/PNG/WebP/GIF/HEIC, enforce ≤ 20 971 520 byte size limit, throw ValidationError with user-friendly message on failure in src/lib/validation/file-validation.ts
- [X] T041 [P] [US3] Implement AlbumService.create() (assign display_order = max + 1000 or 1000), update() (patch name and/or date), and delete() (cascade removes files from disk) in src/lib/services/album-service.ts
- [X] T042 [US3] Implement PhotoService.addPhoto(): run file-validation, save original to data/photos/[albumId]/[uuid].[ext], generate 400×400 JPEG thumbnail via sharp to data/thumbnails/[albumId]/[uuid].jpg, extract width/height from sharp metadata, insert photo row with display_order = max + 1000, set album cover_photo_id if photo is first in album in src/lib/services/photo-service.ts
- [X] T043 [US3] Implement PhotoService.removePhoto(): delete photo DB row, remove original and thumbnail files from disk, update album cover_photo_id to next photo by display_order or NULL if album is now empty in src/lib/services/photo-service.ts
- [X] T044 [US3] Add POST /api/albums handler for album creation (validate name 1–100 chars and ISO date, call AlbumService.create(), return 201 Album) to src/app/api/albums/route.ts
- [X] T045 [US3] Add PUT /api/albums/[id] (patch name/date, return 200 Album) and DELETE /api/albums/[id] (return 204) handlers to src/app/api/albums/[id]/route.ts
- [X] T046 [US3] Implement POST /api/albums/[id]/photos route handler: parse multipart/form-data body, call PhotoService.addPhoto(), return 201 Photo on success or 413/422 with error object on failure in src/app/api/albums/[id]/photos/route.ts
- [X] T047 [US3] Implement DELETE /api/photos/[id] route handler calling PhotoService.removePhoto() and returning 204 in src/app/api/photos/[id]/route.ts
- [X] T048 [P] [US3] Implement ConfirmDialog component: modal overlay with title, message, confirm button, cancel button, accessible focus trap, and Escape to cancel in src/components/ConfirmDialog.tsx
- [X] T049 [US3] Implement CreateAlbumModal component: name text input (1–100 chars, client-side validation), date input, submit calls POST /api/albums, closes and refreshes album list on success in src/components/CreateAlbumModal.tsx
- [X] T050 [US3] Add "Create Album" button and CreateAlbumModal to main page; add per-album delete icon that triggers ConfirmDialog then calls DELETE /api/albums/[id] and refreshes album list in src/app/page.tsx
- [X] T051 [US3] Add "Add Photos" file input (accept image/*, multiple, drag-and-drop onto page) with progress spinner calling POST /api/albums/[id]/photos; add per-tile remove button that triggers ConfirmDialog then calls DELETE /api/photos/[id] in src/app/albums/[id]/page.tsx
- [X] T052 [US3] Write Playwright E2E tests: create album → upload JPEG/PNG/WebP → verify thumbnails appear → upload invalid PDF → verify error message → delete one photo → verify reflow → delete album → verify main page updates in tests/e2e/album-crud.spec.ts

**Checkpoint**: All three user stories independently functional and testable. Full CRUD flow works end-to-end.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Accessibility audits, performance validation, benchmarking, documentation

- [X] T053 [P] Add @axe-core/playwright WCAG 2.1 AA accessibility audits (injectAxe + checkA11y) to album-browse.spec.ts, photo-view.spec.ts, and album-crud.spec.ts
- [X] T054 [P] Add Playwright performance tests: seed 100 albums → assert main page networkidle in < 2 s; seed 500 photos in one album → assert album page tile grid visible in < 3 s in tests/e2e/performance.spec.ts
- [X] T055 [P] Implement thumbnail throughput benchmark in scripts/bench-thumbnails.ts: generate 200 thumbnails from sample.jpg via sharp, compute throughput, assert ≥ 100 thumbnails/s, print result
- [ ] T056 Run all three quickstart.md validation scenarios (S1 browse/reorder, S2 tile view, S3 CRUD) end-to-end and fix any issues discovered
- [X] T057 [P] Create .env.local.example documenting DATABASE_URL, DATA_DIR, and MAX_UPLOAD_SIZE_MB with default values

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — **BLOCKS all user stories**
- **User Story 1 (Phase 3)**: Depends on Foundational; no dependency on US2 or US3
- **User Story 2 (Phase 4)**: Depends on Foundational; no dependency on US1 or US3
- **User Story 3 (Phase 5)**: Depends on Foundational; no dependency on US1 or US2
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Independence Notes

- **US1 testing**: Seed albums via direct DB helper (no UI creation needed)
- **US2 testing**: Seed album + photos via POST /api/albums and POST /api/albums/[id]/photos in Playwright beforeEach
- **US3 testing**: No seeding needed — the story itself implements creation

### Within Each User Story

1. Test tasks written and confirmed **failing** (TDD — mandatory per constitution)
2. Service layer tasks before API route tasks
3. Component tasks before page tasks
4. E2E test tasks last (confirm full story is independently demo-able)

---

## Parallel Opportunities

### Phase 1 (Setup)

```
T001 → T002 → [T003, T004, T005, T006 in parallel]
```

### Phase 2 (Foundational)

```
T007 → T008 → T009          (sequential: schema → migration → connection)

T010, T011, T012             (parallel with T007–T009)

T013 [tests] → T014 [impl]  (after T009)
```

### Phase 3 (US1)

```
T015, T016                   (parallel test writing)
  ↓
T017, T018, T019             (parallel implementations)

T020, T021                   (parallel components)
  ↓
T022 → T023 → T024
```

### Phase 4 (US2)

```
T025, T026                   (parallel test writing)
  ↓
T027, T028, T029, T030       (parallel implementations)

T031 → T032
T033                         (parallel with T031/T032)
  ↓
T034 → T035
```

### Phase 5 (US3)

```
T036, T037, T038             (parallel unit test writing)
  ↓
T039                         (integration tests — depends on T036–T038)
  ↓
T040, T041                   (parallel: file-validation + AlbumService CRUD)
  ↓
T042 → T043                  (PhotoService add then remove)

T044, T045, T046, T047       (parallel API route handlers)

T048, T049                   (parallel UI components)
  ↓
T050 → T051 → T052
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1 (T015–T024)
4. **STOP and VALIDATE**: Seed albums in DB; confirm main page, date grouping, and drag-and-drop work
5. **Demo-able MVP**: Flat album list with date sections and persistent reordering

### Incremental Delivery

1. Setup + Foundational → infrastructure ready
2. User Story 1 → browse and reorder → validate independently → demo
3. User Story 2 → tile grid + lightbox → validate independently → demo
4. User Story 3 → full CRUD → validate independently → demo
5. Polish → accessibility + performance benchmarks → all constitution gates pass

### Parallel Team Strategy

With 3 developers available after Phase 2 completes:

- **Developer A**: User Story 1 (T015–T024)
- **Developer B**: User Story 2 (T025–T035)
- **Developer C**: User Story 3 (T036–T052)
- All converge for Phase 6 Polish

---

## Notes

- `[P]` tasks operate on different files or have no inter-task dependency — safe to parallelise
- `[USn]` label maps each task to its user story for traceability
- Tests MUST be written and confirmed **failing** before implementing the corresponding code (TDD mandate, constitution Principle II)
- Each user story MUST be independently completable and demo-able before moving to the next (constitution Development Workflow)
- Commit after each task or logical group; no "all-in-one" commits (constitution commit discipline)
- `data/` directory is gitignored; created at runtime by `npm run db:migrate`
- Avoid `export const runtime = 'edge'` in any route that imports `src/lib/db/client.ts` — `better-sqlite3` requires Node.js runtime
