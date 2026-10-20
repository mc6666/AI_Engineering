# Implementation Plan: Photo Album Organizer

**Branch**: `001-photo-album-organizer` | **Date**: 2026-06-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-photo-album-organizer/spec.md`

## Summary

A Next.js 15 (App Router) web application for organizing photos into named,
date-tagged albums. Albums are displayed on the main page in date-grouped
sections with drag-and-drop reordering. Photos are stored in a local
directory on the same machine as the Next.js server; only metadata (album
names, dates, display order, file paths) is persisted in a local SQLite
database. Within each album, photos are displayed in a uniform tile grid
with full-size lightbox view. No external services or cloud storage are
used — the app is fully self-contained for single-user local deployment.

## Technical Context

**Language/Version**: TypeScript 5.x, Node.js 20 LTS

**Primary Dependencies**:
- Next.js 15 (App Router, React Server Components, Server Actions)
- `better-sqlite3` ^9 — synchronous SQLite driver for Node.js runtime
- Drizzle ORM — TypeScript-first schema definition and migrations for SQLite
- `@dnd-kit/core` + `@dnd-kit/sortable` — accessible drag-and-drop (React 19 compatible)
- `sharp` ^0.33 — server-side thumbnail generation (libvips, ≥ 100 thumbnails/s)
- Tailwind CSS v4 — utility-first styling

**Storage**: SQLite file at `./data/photo-organizer.db`; original images stored
in `./data/photos/[album-id]/`; generated thumbnails in `./data/thumbnails/[album-id]/`

**Testing**: Jest 29 + ts-jest (unit); Supertest with real SQLite test DB
(integration); Playwright 1.x with axe-core (E2E + accessibility audits)

**Target Platform**: Desktop browsers (Chrome, Firefox, Safari latest);
Node.js 20 localhost server; single-user personal deployment

**Project Type**: Full-stack web application (Next.js monolith — frontend +
API routes in one process)

**Performance Goals**:
- Main page load with 100 albums: < 2 s
- Album view load with 500 photos: < 3 s
- Drag-and-drop reorder + auto-persist: < 1 s end-to-end
- Single photo API operations: < 100 ms
- Thumbnail batch generation: ≥ 100 thumbnails/s
- SQLite query for album list or photo list: < 50 ms

**Constraints**:
- No external network calls for image data (fully local)
- No user authentication (single-user personal deployment)
- Maximum photo file size: 20 MB per file
- Supported formats: JPEG, PNG, WebP, GIF, HEIC
- Node.js runtime only — `better-sqlite3` requires Node.js (no Edge runtime)
- Memory: ≤ 256 MB resident under normal use

**Scale/Scope**: Up to 100 albums, up to 500 photos per album; single
concurrent user; single server process

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I — Code Quality ✅

TypeScript strict mode enforces explicit type signatures on all public APIs
and service interfaces. Drizzle ORM provides end-to-end type safety from
schema to query result. ESLint + `eslint-plugin-sonarjs` will enforce
cyclomatic complexity ≤ 10 per function at CI time. All dependencies are
justified: Next.js (framework), better-sqlite3 (local DB), @dnd-kit
(accessible drag-and-drop), sharp (thumbnail performance), Tailwind
(styling without runtime overhead).

### Principle II — Testing Standards ✅

TDD plan — tests written first, confirmed failing, then implemented:

- **Unit** (Jest + ts-jest): `album-service`, `photo-service`,
  `file-validation` — pure logic, no I/O mocking
- **Integration** (Supertest): all API routes tested against a real
  SQLite `test.db` (no mocked DB, no mocked filesystem); real image
  fixtures from `tests/fixtures/images/`
- **E2E** (Playwright): album browse, drag-and-drop reorder, photo tile
  grid, lightbox navigation, album/photo deletion
- **Accessibility** (axe-core in Playwright): WCAG 2.1 AA audit on each
  page after interaction

Coverage threshold: ≥ 80% line coverage enforced by Jest
`coverageThreshold` config; build fails below threshold.

### Principle III — UX Consistency ✅

- `@dnd-kit` provides ARIA drag-and-drop roles and keyboard navigation
  (Space to grab, arrow keys to move, Enter/Space to drop)
- Progress feedback: thumbnail generation triggers a spinner overlay
  (operation typically > 200 ms per photo)
- Image tiles use `next/image` blur placeholder while loading
- WCAG 2.1 AA verified by axe-core in Playwright E2E suite
- Terminology: "album" and "photo" used consistently in UI, API responses,
  error messages, and documentation — no synonyms

### Principle IV — Performance Requirements ✅

Performance measurement strategy:
1. `performance.now()` timers in all API route handlers, logged to console
   in development
2. SQLite composite index on `(album_id, display_order)` for photo queries;
   index on `display_order` for album list; index on `date` for grouping
3. Playwright E2E benchmark test seeds 100 albums / 500 photos and
   asserts network idle within spec thresholds via `page.waitForLoadState`
4. `npm run bench:thumbnails` — standalone script generating 200 thumbnails
   with `sharp`, reporting throughput; must print ≥ 100/s
5. Lighthouse CI in E2E pipeline for frontend performance score

All success criteria in spec.md map to constitution Principle IV thresholds.

*Post-Phase 1 re-check*: fractional-index reorder design (single row update)
and thumbnail-on-add strategy (pre-computed, immutably cached) satisfy
performance constraints with margin. No gate violations found.

## Project Structure

### Documentation (this feature)

```text
specs/001-photo-album-organizer/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── api.md           # Phase 1 output — REST API contracts
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
src/
├── app/
│   ├── layout.tsx                     # Root layout, global font + metadata
│   ├── page.tsx                       # Main page: date-grouped album grid
│   ├── globals.css
│   └── albums/
│       └── [id]/
│           └── page.tsx               # Album view: photo tile grid
├── app/api/
│   ├── albums/
│   │   ├── route.ts                   # GET /api/albums, POST /api/albums
│   │   └── [id]/
│   │       ├── route.ts               # GET, PUT, DELETE /api/albums/[id]
│   │       ├── reorder/
│   │       │   └── route.ts           # POST /api/albums/[id]/reorder
│   │       └── photos/
│   │           └── route.ts           # POST /api/albums/[id]/photos
│   └── photos/
│       └── [id]/
│           ├── route.ts               # DELETE /api/photos/[id]
│           ├── image/
│           │   └── route.ts           # GET /api/photos/[id]/image
│           └── thumbnail/
│               └── route.ts           # GET /api/photos/[id]/thumbnail
├── components/
│   ├── AlbumGrid.tsx                  # @dnd-kit sortable wrapper
│   ├── AlbumCard.tsx                  # Single album card (name, date, cover)
│   ├── PhotoGrid.tsx                  # Tile grid container
│   ├── PhotoTile.tsx                  # Individual photo tile with lazy image
│   ├── LightboxOverlay.tsx            # Full-size view + prev/next navigation
│   ├── EmptyState.tsx                 # Shared empty-state component
│   ├── ConfirmDialog.tsx              # Reusable delete confirmation modal
│   └── CreateAlbumModal.tsx           # Album creation form
├── lib/
│   ├── db/
│   │   ├── schema.ts                  # Drizzle ORM table definitions
│   │   ├── client.ts                  # Singleton better-sqlite3 connection
│   │   └── migrations/                # Drizzle-generated SQL migrations
│   ├── services/
│   │   ├── album-service.ts           # Album CRUD + fractional-index reorder
│   │   └── photo-service.ts           # Photo add, remove, serve, thumbnail
│   └── validation/
│       └── file-validation.ts         # Magic-byte MIME check, size guard
└── types/
    └── index.ts                       # Shared Album, Photo, ApiError types

data/                                  # Runtime data (gitignored)
├── photo-organizer.db
├── photos/
│   └── [album-id]/[uuid].[ext]
└── thumbnails/
    └── [album-id]/[uuid].jpg

tests/
├── unit/
│   ├── services/
│   │   ├── album-service.test.ts
│   │   └── photo-service.test.ts
│   └── validation/
│       └── file-validation.test.ts
├── integration/
│   └── api/
│       ├── albums.test.ts
│       └── photos.test.ts
├── e2e/
│   ├── album-browse.spec.ts
│   ├── album-reorder.spec.ts
│   └── photo-view.spec.ts
└── fixtures/
    └── images/                        # Committed sample images for tests
        ├── sample.jpg
        ├── sample.png
        ├── sample.webp
        └── invalid.pdf                # Used to test rejection
```

**Structure Decision**: Single Next.js 15 monolith with App Router. API
routes co-located in `src/app/api/` alongside page routes. Library code
in `src/lib/` (DB schema, services, validation) is shared between API
routes and any server actions. This avoids a separate backend project while
keeping concerns clearly separated by directory.

## Complexity Tracking

> No constitution violations — complexity table not required.
