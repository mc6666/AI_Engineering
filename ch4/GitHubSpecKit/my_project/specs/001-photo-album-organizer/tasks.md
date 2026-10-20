---

description: "Task list for Photo Album Organizer implementation"
---

# Tasks: Photo Album Organizer

**Input**: Design documents from `/specs/001-photo-album-organizer/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/ui-contracts.md ✅

**Tests**: Included per constitution Principle II (Test-First Development is non-negotiable). Tests
are written and confirmed FAILING before each implementation task.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story this task belongs to (US1–US4)
- Every task includes an exact file path

## Path Conventions

Single project layout per plan.md:
- Source: `src/` (models/, services/, ui/pages/, ui/components/)
- Tests: `tests/unit/`, `tests/integration/`
- Data: `data/`, `thumbnails/`, `photos/`

---

## Phase 1: Setup

**Purpose**: Project initialization — directory structure, dependencies, and tooling

- [x] T001 Create project directory structure: `src/models/`, `src/services/`, `src/ui/pages/`, `src/ui/components/`, `tests/unit/`, `tests/integration/`, `data/`, `thumbnails/`, `photos/`
- [x] T002 Create `requirements.txt` with pinned dependencies: `nicegui>=1.4`, `pillow>=10.0`, `aiosqlite>=0.19`, `pytest>=7.0`, `pytest-asyncio`
- [x] T003 [P] Create `pyproject.toml` with ruff linting configuration (line-length=100, select E/W/F, ignore E501)
- [x] T004 [P] Add `.gitkeep` to `data/`, `thumbnails/`, `photos/`; add those directories to `.gitignore`; add `__init__.py` to all `src/` and `tests/` packages

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models, database layer, and app skeleton — MUST be complete before any user
story work begins.

**⚠️ CRITICAL**: No user story phase can start until this phase is complete.

- [x] T005 [P] Write unit tests for Album dataclass in `tests/unit/test_album_model.py` — test field defaults, ISO date validation, and that `id` is nullable before DB insertion; verify tests FAIL
- [x] T006 [P] Write unit tests for Photo dataclass in `tests/unit/test_photo_model.py` — test field defaults, nullable `date_taken`, and `thumbnail_path` starts as None; verify tests FAIL
- [x] T007 Create `src/models/album.py` — `Album` dataclass with fields: `id`, `label`, `date`, `cover_photo_id`, `display_order`, `created_at` (matches data-model.md schema)
- [x] T008 [P] Create `src/models/photo.py` — `Photo` dataclass with fields: `id`, `filename`, `file_path`, `date_taken`, `import_date`, `file_size`, `album_id`, `thumbnail_path`
- [x] T009 Write integration test for DB schema creation in `tests/integration/test_db_migrations.py` — assert both `albums` and `photos` tables exist with correct columns and unique indexes after `db.init()` call; verify tests FAIL
- [x] T010 Create `src/services/db.py` — async `init(db_path)` that opens an `aiosqlite` connection, runs the full DDL from data-model.md (albums + photos tables, all indexes), and exposes a module-level connection handle
- [x] T011 Create `src/main.py` — NiceGUI app entry point: call `db.init()` on startup, mount `app.add_media_files('/photos', 'photos/')` and `app.add_media_files('/thumbnails', 'thumbnails/')`, register page routes `@ui.page('/')` and `@ui.page('/album/{album_id}')` as stubs, call `ui.run()`

**Checkpoint**: `pytest tests/` passes for T005–T009. `python src/main.py` starts without errors. DB file created in `data/`.

---

## Phase 3: User Story 2 — View Albums on Main Page (Priority: P1) 🎯 MVP Foundation

**Goal**: Main page renders all albums from the database as cards with labels and cover thumbnails.
Empty-state message shown when no albums exist.

**Independent Test**: Seed 3 albums directly in SQLite (`INSERT INTO albums ...`); open
`http://localhost:8080`; verify 3 album cards render, each with a date label; verify empty-state
message appears when the table is empty.

### Tests for User Story 2 ⚠️ Write FIRST — verify FAIL before implementing

- [x] T012 Write unit tests for `AlbumService.get_all_albums()` in `tests/unit/test_album_service.py` — assert returns albums ordered by `display_order` ASC, returns empty list when no albums exist; verify tests FAIL

### Implementation for User Story 2

- [x] T013 Implement `AlbumService.get_all_albums()` in `src/services/album_service.py` — async method querying `SELECT * FROM albums ORDER BY display_order ASC`, returning list of `Album` dataclass instances
- [x] T014 [P] Create `src/ui/components/album_card.py` — NiceGUI component rendering: cover thumbnail (`/thumbnails/{photo_id}.jpg` or placeholder icon if None), album label below, `data-album-id` HTML attribute, click navigates to `/album/{album_id}`
- [x] T015 Implement main page album grid in `src/ui/pages/main_page.py` — `@ui.page('/')` handler: call `AlbumService.get_all_albums()`, render empty-state `ui.label` if list is empty, otherwise render one `AlbumCard` per album in a responsive `ui.grid`; wire `main_page` into `src/main.py`

**Checkpoint**: Main page shows album cards from seeded database. Empty state confirmed.

---

## Phase 4: User Story 1 — Upload Photos into Date-Based Albums (Priority: P1) 🎯 MVP Core

**Goal**: User can import photos via file picker; photos are grouped into date albums by EXIF date;
thumbnails generated; main page shows updated albums after import.

**Independent Test**: Click "Import Photos", select 3 JPEGs with known dates (2024-06-15,
2024-06-16, 2024-06-15). Verify: 2 albums created, first album has 2 photos, no duplicate albums
for 2024-06-15, thumbnails generated in `thumbnails/`.

### Tests for User Story 1 ⚠️ Write FIRST — verify FAIL before implementing

- [x] T016 [P] Write unit tests for `PhotoService.import_photo()` in `tests/unit/test_photo_service.py` — test EXIF date extraction from a fixture JPEG, fallback to today when no EXIF, correct album assignment, rejection of non-image files; verify tests FAIL
- [x] T017 [P] Write unit tests for `ThumbnailService.generate()` in `tests/unit/test_thumbnail_service.py` — assert output is 256×256 JPEG, cached at `thumbnails/{photo_id}.jpg`, idempotent on re-call; verify tests FAIL
- [x] T018 Write integration test for full import flow in `tests/integration/test_import_flow.py` — upload 3 image fixtures, assert correct album count, correct photo-to-album assignment, thumbnails on disk, `cover_photo_id` set on album; verify tests FAIL

### Implementation for User Story 1

- [x] T019 Implement `AlbumService` write operations in `src/services/album_service.py` — add `get_or_create_by_date(date_str)` (returns existing or creates new album), `update_cover_photo(album_id, photo_id)`, and `create_album(label, date, display_order)`
- [x] T020 Create `src/services/thumbnail_service.py` — `async generate(photo_id, source_path)` opens image with Pillow, resizes to 256×256 with center-crop, saves as JPEG to `thumbnails/{photo_id}.jpg`, returns thumbnail path
- [x] T021 Create `src/services/photo_service.py` — `async import_photo(filename, file_bytes)`: validate format (JPEG/PNG/GIF/WEBP), save bytes to `photos/` with collision-safe filename, extract EXIF `DateTimeOriginal`/`DateTime` → ISO date (fallback to today), call `AlbumService.get_or_create_by_date()`, insert photo record in DB, call `ThumbnailService.generate()`, update album `cover_photo_id` if not set; return `Photo` instance
- [x] T022 Add import handler to `src/ui/pages/main_page.py` — add `ui.upload(multiple=True, on_upload=handle_import, on_rejected=handle_reject)` to page; `handle_import` calls `PhotoService.import_photo()` for each file and refreshes album grid; `handle_reject` calls `ui.notify(f"'{name}' is not a supported image format...", type='negative')`

**Checkpoint**: Upload 3 photos → correct date albums created → thumbnails in `thumbnails/` → main page updates.

---

## Phase 5: User Story 4 — Browse Photos Inside an Album (Priority: P1)

**Goal**: Clicking an album opens a tile grid of all its photos. Clicking a tile shows a lightbox
overlay. Album label is editable inline. Back navigation returns to main page.

**Independent Test**: Seed an album with 5 photos in SQLite; navigate directly to
`/album/{id}`; verify 5 tiles render; click first tile; verify lightbox with full image opens;
press Escape; verify lightbox closes; click "← Albums"; verify redirect to `/`.

### Tests for User Story 4 ⚠️ Write FIRST — verify FAIL before implementing

- [x] T023 [P] Write unit tests for `PhotoService.get_photos_by_album(album_id)` in `tests/unit/test_photo_service.py` — assert returns photos ordered by `date_taken` ASC then `import_date` ASC, returns empty list for unknown album; verify tests FAIL
- [x] T024 [P] Write unit tests for `AlbumService.update_label(album_id, new_label)` in `tests/unit/test_album_service.py` — assert label updated in DB, returns updated `Album`; verify tests FAIL

### Implementation for User Story 4

- [x] T025 Add `PhotoService.get_photos_by_album(album_id)` to `src/services/photo_service.py` — async SELECT ordered by `date_taken` ASC, `import_date` ASC
- [x] T026 Add `AlbumService.update_label(album_id, new_label)` to `src/services/album_service.py` — async UPDATE label field
- [x] T027 [P] Create `src/ui/components/photo_tile.py` — NiceGUI component: `ui.image(thumbnail_url)` in a 256×256 square container, `object-fit: cover`, emits click event with `photo_id`
- [x] T028 [P] Create `src/ui/components/lightbox.py` — NiceGUI component: full-viewport semi-transparent overlay, centered `ui.image(photo_url)` constrained to 90% viewport, close button + click-outside handler + Escape key binding via `ui.keyboard`
- [x] T029 Implement `src/ui/pages/album_page.py` — `@ui.page('/album/{album_id}')`: redirect to `/` with `ui.notify` if album not found; render "← Albums" back link, editable album label (calls `AlbumService.update_label` on change), responsive `ui.grid` of `PhotoTile` components from `PhotoService.get_photos_by_album`; tile click opens `Lightbox`; wire page into `src/main.py`

**Checkpoint**: Album page renders tiles, lightbox opens/closes, label editing persists, back navigation works.

---

## Phase 6: User Story 3 — Drag-and-Drop Album Reordering (Priority: P2)

**Goal**: Albums on the main page are reorderable via drag-and-drop using SortableJS. The new
order persists across page reloads.

**Independent Test**: With 3+ albums on main page, drag the last album to first position and
release; refresh the page; confirm the dragged album is now first.

### Tests for User Story 3 ⚠️ Write FIRST — verify FAIL before implementing

- [x] T030 Write unit tests for `AlbumService.update_display_order(ordered_ids)` in `tests/unit/test_album_service.py` — assert each album's `display_order` is set to its index in the list, gaps removed after operation; verify tests FAIL

### Implementation for User Story 3

- [x] T031 Add `AlbumService.update_display_order(ordered_ids)` to `src/services/album_service.py` — async bulk UPDATE setting `display_order = index` for each `album_id` at position `index` in `ordered_ids`
- [x] T032 Add `POST /api/albums/reorder` FastAPI route to `src/main.py` — accepts `{ "ordered_ids": [...] }`, calls `AlbumService.update_display_order`, returns `{ "status": "ok" }` (200) or 422 on unknown IDs
- [x] T033 Integrate SortableJS into `src/ui/pages/main_page.py` — inject SortableJS CDN via `ui.add_head_html()`; after album grid renders, call `ui.run_javascript()` to initialize `new Sortable(container, { animation: 150, onEnd: sendOrderToServer })`; `sendOrderToServer` reads `data-album-id` attributes from sorted DOM order and POSTs to `/api/albums/reorder`

**Checkpoint**: All 4 user stories are independently functional. Reorder persists after refresh.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Cross-cutting improvements affecting multiple user stories

- [x] T034 [P] Add startup thumbnail repair scan to `src/services/thumbnail_service.py` — on app start, query photos with NULL `thumbnail_path` or missing thumbnail file and regenerate them in the background
- [x] T035 [P] Add duplicate file detection to `src/services/photo_service.py` — before saving, check `file_path` uniqueness in DB; if duplicate, skip and notify user "'{filename}' was already imported"
- [x] T036 Run `ruff check src/ tests/` and fix all lint errors
- [x] T037 [P] Run full test suite `pytest tests/ -v` and confirm all tests pass
- [ ] T038 Run all validation scenarios from `specs/001-photo-album-organizer/quickstart.md` end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **US2 Main Page Display (Phase 3)**: Depends on Phase 2 — no dependency on other user stories
- **US1 Photo Import (Phase 4)**: Depends on Phase 2 — builds on Phase 3 main page (adds upload handler)
- **US4 Album Tile View (Phase 5)**: Depends on Phase 2 — can run in parallel with Phase 3 and 4
- **US3 Drag-and-Drop (Phase 6)**: Depends on Phase 3 (main page must exist)
- **Polish (Phase N)**: Depends on all user story phases

### User Story Dependencies

- **US2 (Phase 3)**: After Phase 2 — first user story to implement
- **US1 (Phase 4)**: After Phase 2 — can run in parallel with US2 on separate team members
- **US4 (Phase 5)**: After Phase 2 — can run in parallel with US2/US1
- **US3 (Phase 6)**: After US2 (needs main page) — sequential to Phase 3

### Within Each User Story

- Tests MUST be written and confirmed FAILING before implementation begins
- Services before UI components
- Components before pages
- Core implementation before integration tasks

### Parallel Opportunities

- T005 and T006 (model tests) — parallel
- T007 and T008 (model implementations) — parallel after T005/T006
- T016, T017 (service unit tests) — parallel within Phase 4
- T023, T024 (service unit tests) — parallel within Phase 5
- T027, T028 (UI components) — parallel within Phase 5
- T034, T035, T037 — parallel in Polish phase

---

## Parallel Execution Example: Phase 4 (US1)

```bash
# Launch all US1 tests in parallel (write first, before any implementation):
Task T016: "Write PhotoService unit tests in tests/unit/test_photo_service.py"
Task T017: "Write ThumbnailService unit tests in tests/unit/test_thumbnail_service.py"

# After tests fail, implement in parallel where possible:
Task T020: "Create src/services/thumbnail_service.py"   # Independent
Task T019: "Add AlbumService write ops"                  # Independent of thumbnail
# T021 (photo_service.py) depends on T019 and T020 — run after both complete
```

---

## Implementation Strategy

### MVP First (US2 + US1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: US2 — main page renders albums from DB
4. Complete Phase 4: US1 — upload photos → albums created → appear on main page
5. **STOP AND VALIDATE**: Seed data, import photos, verify main page — this is a working MVP
6. Deploy / demo if ready

### Incremental Delivery

1. Setup + Foundational → skeleton app running
2. US2 → main page with album cards (verify with seeded data)
3. US1 → photo import working (full import flow)
4. US4 → album tile grid + lightbox
5. US3 → drag-and-drop reordering
6. Polish → lint, tests passing, quickstart validated

### Parallel Team Strategy

After Phase 2 completes:

- Developer A: Phase 3 (US2 — main page display)
- Developer B: Phase 4 (US1 — photo import services)
- Developer C: Phase 5 (US4 — album tile view + lightbox)
- All converge for Phase 6 (US3 — drag-and-drop, needs main page from A)

---

## Notes

- **[P]** = tasks operate on different files; safe to parallelize
- **[Story]** maps each task to its user story for traceability
- Constitution Principle II mandates TDD — test tasks MUST run before their implementation tasks
- Tests that don't exist yet should be created, run to confirm failure, then implementation proceeds
- Commit after each completed checkpoint (not after every individual task)
- Do not start Phase 3 until `pytest tests/integration/test_db_migrations.py` passes
