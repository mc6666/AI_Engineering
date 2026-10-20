# Research: Photo Album Organizer

**Feature**: Photo Album Organizer
**Date**: 2026-06-15
**Status**: Complete — all technical decisions resolved

## 1. Next.js 15 App Router + SQLite

**Decision**: Next.js 15 App Router with `better-sqlite3` accessed exclusively
in Server Components and API Route Handlers (Node.js runtime). Drizzle ORM
provides typed schema and migration management.

**Rationale**:
- `better-sqlite3` is synchronous, which aligns naturally with Next.js API route
  handlers and Server Actions — no async connection pool management needed
- Drizzle ORM is TypeScript-first with minimal overhead; unlike Prisma it has no
  binary engine and generates plain SQL migrations readable without tooling
- A single SQLite file at `./data/photo-organizer.db` is the correct persistence
  model for a single-user local application — no server, no connection strings

**Alternatives considered**:
- **Prisma + SQLite**: Heavier binary engine, async-only API, overkill for a
  personal local deployment
- **sql.js (WASM SQLite)**: Runs in the browser; not applicable for server-side
  data that must survive page reloads
- **PostgreSQL / MySQL**: Requires a running database server process; adds
  infrastructure complexity with no benefit for single-user local use

**Constraint**: `better-sqlite3` requires the Node.js runtime (not Edge). All
API routes that touch the DB must use the Node.js runtime (the App Router
default), so no explicit `export const runtime = 'edge'` declarations.

---

## 2. Drag-and-Drop Library

**Decision**: `@dnd-kit/core` + `@dnd-kit/sortable`

**Rationale**:
- Actively maintained (releases throughout 2024), compatible with React 19
- First-class accessibility: ARIA `role="button"` on drag handles, keyboard
  navigation (Space to pick up, Arrow keys to move, Enter/Escape to drop/cancel),
  screen-reader announcements built in
- Modular: only the two packages needed; tree-shakeable; no monolithic bundle
- Works well with the fractional-index reorder strategy — `useSortable` exposes
  the `over` and `active` IDs to compute new display_order values

**Alternatives considered**:
- **react-beautiful-dnd**: Last release April 2022; marked as not recommended for
  new projects by the maintainer; incompatible with React 18+ StrictMode
- **@hello-pangea/dnd** (maintained rbd fork): Works but ARIA support is weaker;
  less active development compared to @dnd-kit
- **Native HTML5 drag-and-drop**: No accessibility (no keyboard support), poor
  and inconsistent touch support, complex cross-browser implementation

---

## 3. Image Serving from Local Filesystem

**Decision**: Custom API route handlers `GET /api/photos/[id]/image` and
`GET /api/photos/[id]/thumbnail` read files from the `data/` directory and
stream them as HTTP responses with appropriate `Content-Type` and cache headers.

**Rationale**:
- `next/image` requires statically known remote patterns or static file imports;
  dynamically addressed local filesystem paths from a database are not directly
  supported by the optimizer
- A thin API streaming route is sufficient and correct: resolve path from DB
  record → guard against path traversal → `fs.createReadStream` → pipe to
  `NextResponse`
- Immutable cache headers (`Cache-Control: public, max-age=31536000, immutable`)
  on thumbnail routes eliminate redundant reads after first load

**Security note**: File path from the DB record is stored as a relative path
under `data/`; the API route resolves it with `path.join(DATA_DIR, filepath)`
and validates the result starts with `DATA_DIR` to prevent path traversal.

---

## 4. Thumbnail Generation

**Decision**: `sharp` ^0.33 — server-side thumbnail generation at photo-add time.
Thumbnails: 400×400 px, `fit: 'cover'` (center crop), JPEG output, quality 80.

**Rationale**:
- `sharp` (libvips-based) consistently delivers ≥ 100 thumbnails/s on modern
  hardware — exceeds the constitution Principle IV batch throughput requirement
- Thumbnails generated once at upload time and stored as immutable files;
  no repeated CPU work on subsequent page loads
- 400×400 JPEG at quality 80 is ~30–50 KB per thumbnail; 500 thumbnails ≈ 15–25 MB

**HEIC/HEIF support**: `sharp` handles HEIC input natively on most platforms;
on platforms where libheif is not bundled, a pre-processing step using
`heic-convert` converts to JPEG before passing to `sharp`.

**Alternatives considered**:
- **`jimp`** (pure JS): ~10 thumbnails/s on the same hardware; fails the
  ≥ 100/s constitution throughput requirement by an order of magnitude
- **On-the-fly generation per request**: No disk caching; repeated CPU cost per
  page load; unacceptable for an album with 500 photos
- **Client-side canvas resize**: Requires sending the full original to the
  browser first, defeating the local-storage design goal

---

## 5. Album Reorder Persistence — Fractional Indexing

**Decision**: Store `display_order` as SQLite `REAL` (IEEE 754 double). New
albums default to `(max_existing + 1000)`. On drag-drop, update only the moved
item to `(predecessor_order + successor_order) / 2`. Renormalize all orders to
`index × 1000` when any gap shrinks below 0.001.

**Rationale**:
- O(1) single-row UPDATE per reorder — no shifting of adjacent rows, no
  cascading writes
- REAL has ~15 significant decimal digits; gaps below 0.001 require
  approximately 2^40 reorders between the same two items — renormalization
  is a rare edge case in practice
- The same strategy applies to photo `display_order` within an album

**Boundary cases**:
- Album moved to start: new order = `first_order - 500` (or 500 if list was empty)
- Album moved to end: new order = `last_order + 1000`

**Alternatives considered**:
- **Integer ranks with gaps (1000, 2000, 3000)**: Same principle but gaps run
  out faster and renormalization is O(n) writes
- **Sequential integer position**: Every reorder updates O(n) rows in the table

---

## 6. File Validation

**Decision**: Validate MIME type server-side using magic bytes (first 12 bytes
of the file buffer), independent of the browser-supplied `Content-Type` header.

**Magic byte signatures checked**:

| Format | Signature |
|--------|-----------|
| JPEG | `FF D8 FF` |
| PNG | `89 50 4E 47 0D 0A 1A 0A` |
| WebP | `52 49 46 46 ?? ?? ?? ?? 57 45 42 50` |
| GIF | `47 49 46 38` |
| HEIC/HEIF | ftyp box at offset 4: `68 65 69 63` or `68 65 69 66` |

**Rationale**:
- Browser-supplied `Content-Type` can be incorrect (e.g., a JPEG reported as
  `application/octet-stream`) or spoofed
- Magic byte check is definitive and adds one read of 12 bytes — negligible cost
- `sharp` throws on non-image input as a secondary defense; pre-check gives a
  user-friendly error message before the more expensive `sharp` call

**Allowed MIME types**: `image/jpeg`, `image/png`, `image/webp`, `image/gif`,
`image/heic`, `image/heif`

---

## 7. Testing Stack

**Decision**:
- **Unit**: Jest 29 + `ts-jest` for service and validation logic
- **Integration**: Supertest against real Next.js route handlers, real SQLite
  at `./data/test.db` (reset before each suite), real image fixtures
- **E2E**: Playwright 1.x — browser automation; `@axe-core/playwright` for
  WCAG 2.1 AA accessibility audits on each page
- **Coverage**: Jest `--coverage` with `coverageThreshold: { global: { lines: 80 } }`

**Test data strategy**:
- `tests/fixtures/images/` contains committed sample files:
  `sample.jpg`, `sample.png`, `sample.webp`, `sample.gif`, `invalid.pdf`
- Integration tests use a separate `test.db` deleted and recreated before each
  test file runs (Jest `globalSetup` / `beforeAll`)
- Playwright E2E tests call the API directly to seed data, then clean up in
  `afterEach`

**Rationale**:
- Constitution Principle II mandates no mocking of the filesystem, DB, or photo
  APIs in integration tests — real fixtures and a real test DB satisfy this
- Playwright is required for drag-and-drop E2E validation; `jsdom` cannot
  simulate pointer events at the level needed for `@dnd-kit`

---

## Resolved Decisions Summary

| Topic | Decision | Status |
|-------|----------|--------|
| Framework | Next.js 15 App Router | ✅ |
| Database driver | better-sqlite3 + Drizzle ORM | ✅ |
| Drag-and-drop | @dnd-kit/core + @dnd-kit/sortable | ✅ |
| Image serving | Custom API streaming route | ✅ |
| Thumbnails | sharp, 400×400 JPEG, generated at add time | ✅ |
| Reorder algorithm | Fractional indexing (REAL column) | ✅ |
| File validation | Magic bytes server-side | ✅ |
| Testing stack | Jest + Supertest + Playwright | ✅ |

No NEEDS CLARIFICATION items remain.
