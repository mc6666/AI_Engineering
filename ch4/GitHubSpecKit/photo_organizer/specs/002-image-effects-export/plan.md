# Implementation Plan: Image Processing with Special Effects & Export

**Branch**: `002-image-effects-export` | **Date**: 2026-06-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-image-effects-export/spec.md`

## Summary

Adds a non-destructive image effects system to the existing Next.js 15 photo organizer. Users open an effects panel on any photo, choose from a curated set of visual effects (color filters, tone adjustments, artistic styles), and preview the result instantly via CSS filters in the browser. When satisfied, they download the processed photo or batch-export an album as a ZIP archive. Effect pipelines are applied server-side with `sharp` — the same library already used for thumbnail generation — so no new binary dependencies are required beyond `archiver` for ZIP creation. No new database tables are needed; the effect chain is request-scoped and fully non-destructive.

## Technical Context

**Language/Version**: TypeScript 5.x, Node.js 20 LTS (no change from spec 001)

**Primary Dependencies**:
- All existing: Next.js 15, sharp ^0.33, better-sqlite3 ^9, Drizzle ORM, Tailwind CSS v3
- **New**: `archiver` ^7 — streaming ZIP creation for batch export (Node.js native streams)
- **New dev**: `@types/archiver` ^5

**Storage**: No new tables. No new columns on `photos` or `albums`. Effect chains are ephemeral (request body). ZIP archives are streamed in-memory — never written to disk.

**Testing**: Jest 29 + ts-jest (unit); Supertest with real SQLite test DB (integration); Playwright 1.x with axe-core (E2E + accessibility)

**Target Platform**: Desktop browsers (Chrome, Firefox, Safari latest); Node.js 20 localhost server (no change)

**Project Type**: Full-stack Next.js 15 monolith (no change)

**Performance Goals**:
- CSS filter preview update: ≤ 16 ms (browser-native, zero server round-trips)
- Single photo process + download: ≤ 5 s for photos up to 20 MB
- Sharp effect pipeline per photo: ≤ 200 ms on reference hardware (quad-core CPU, SSD)
- Batch export throughput: ≥ 10 photos/s (ZIP I/O is the bottleneck; constitution IV's 100 photos/s applies to thumbnail pipeline)
- Batch export cancellation cleanup: ≤ 2 s
- Memory during 100-photo export: ≤ 256 MB resident (photos processed sequentially, not held in memory simultaneously)

**Constraints** (inherited + additions):
- Original photo files MUST NOT be modified (non-destructive)
- Max effect chain depth: 5 effects per photo
- Export formats: JPEG and PNG only (WEBP, TIFF, HEIC out of scope)
- Batch export scoped to one album or explicit photo id list
- Node.js runtime only (sharp requires it)
- No external network calls; fully local

**Scale/Scope**: Same as spec 001 — up to 100 albums, 500 photos per album; single concurrent user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I — Code Quality ✅

`effect-service.ts` is a pure function (buffer → EffectParam[] → buffer) with a single responsibility. `export-service.ts` orchestrates ZIP creation, delegating all effect work to `effect-service`. TypeScript strict mode enforces explicit types on all public function signatures. ESLint sonarjs complexity rule (≤ 10 per function) is enforced at CI time. `archiver` is the minimum viable new dependency for streaming ZIP; no higher-level wrappers needed.

### Principle II — Testing Standards ✅

TDD — tests written first per constitution mandate:

- **Unit** (Jest): `effect-service.test.ts` — tests each effect type against real fixture images using real `sharp` (no mocking); verifies output buffer is a valid image and visually differs from input
- **Integration** (Supertest): `process.test.ts` and `export.test.ts` — call all new API routes against a real SQLite test DB with real image fixtures; verify HTTP status, `Content-Type`, and that the response body decodes as a valid image or ZIP
- **E2E** (Playwright): effects panel opens; selecting an effect applies a CSS filter within 500 ms; Download triggers a file save; Export Album downloads a `.zip`

### Principle III — UX Consistency ✅

- Effects panel uses the same Tailwind utility classes and focus-ring pattern as `ConfirmDialog` and `CreateAlbumModal`
- Every export operation (single download and batch) displays `ExportProgress` feedback — consistent with the constitution's 200 ms progress rule
- Effect tiles and intensity sliders are keyboard-accessible (Tab to focus, Enter/Space to activate, arrow keys on sliders); axe-core audit added to `photo-effects.spec.ts`
- Terminology: "effect", "download", "export", "album" — matches all existing UI labels; no synonyms introduced

### Principle IV — Performance Requirements ✅

Performance measurement strategy:
1. `performance.now()` around `applyEffects()` in each API route handler, logged in development
2. `scripts/bench-effects.ts` — processes 100 photos with each effect type via `sharp`, reports per-effect throughput; must sustain ≥ 10 photos/s including ZIP I/O
3. Photos in `export-service` are processed sequentially with `Buffer` released after each photo is piped into the archive, keeping resident memory flat
4. Playwright E2E asserts preview CSS filter appears within 500 ms of effect tile click
5. Lighthouse CI already in E2E pipeline from spec 001; no regression expected (effects panel is rendered on demand, not on page load)

*Post-Phase 1 re-check*: CSS filter preview eliminates all server round-trips for SC-001. Sequential ZIP pipelining keeps memory ≤ 256 MB. No gate violations.

## Project Structure

### Documentation (this feature)

```text
specs/002-image-effects-export/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── api.md           # Phase 1 output — new process + export API contracts
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (additions to existing src/)

```text
src/
├── app/api/
│   ├── photos/
│   │   ├── [id]/
│   │   │   └── process/
│   │   │       └── route.ts           # POST /api/photos/[id]/process
│   │   └── export/
│   │       └── route.ts               # POST /api/photos/export (selection ZIP)
│   └── albums/
│       └── [id]/
│           └── export/
│               └── route.ts           # POST /api/albums/[id]/export (album ZIP)
├── components/
│   ├── EffectsPanel.tsx               # Effect tiles + intensity slider
│   ├── EffectPreview.tsx              # Photo with CSS filter applied live
│   └── ExportDialog.tsx               # Format selector, download/export trigger + progress
├── lib/
│   └── services/
│       ├── effect-service.ts          # Builds and applies sharp pipeline from EffectParam[]
│       └── export-service.ts          # Orchestrates batch ZIP via archiver
└── types/
    └── index.ts                       # Adds EffectType, EffectParam, OutputFormat, ExportRequest

tests/
├── unit/
│   └── services/
│       └── effect-service.test.ts     # Per-effect pipeline + chain-of-5 tests
├── integration/
│   └── api/
│       ├── process.test.ts            # POST /api/photos/[id]/process
│       └── export.test.ts             # POST /api/photos/export + /api/albums/[id]/export
└── e2e/
    └── photo-effects.spec.ts          # Panel → preview → download → album export flow
```

**Structure Decision**: Single Next.js 15 monolith (same as spec 001). New API routes slot directly into the existing `src/app/api/` hierarchy alongside spec 001 routes. New components follow the same co-location pattern as existing components. No additional packages, projects, or process boundaries introduced.

## Complexity Tracking

> No constitution violations — complexity table not required.
