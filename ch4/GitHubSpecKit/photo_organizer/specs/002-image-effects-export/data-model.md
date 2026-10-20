# Data Model: Image Processing with Special Effects & Export

**Feature**: Image Effects & Export
**Date**: 2026-06-17

## Overview

This feature adds no new database tables or columns. All effect state is ephemeral and request-scoped. The data model consists entirely of new TypeScript types added to `src/types/index.ts`.

---

## New TypeScript Types

### `EffectType`

An enumeration of the eight supported visual effects.

```typescript
export type EffectType =
  | 'grayscale'
  | 'sepia'
  | 'vintage'
  | 'blur'
  | 'sharpen'
  | 'brightness'
  | 'contrast'
  | 'saturation';
```

**Invariants**:
- Exactly 8 members; extending requires a plan amendment.
- `vintage` has no adjustable intensity parameter (it is a fixed compound preset).

---

### `EffectParam`

Describes a single effect in an effect chain, including its user-configured intensity.

```typescript
export interface EffectParam {
  type: EffectType;
  intensity: number; // integer 0–100
}
```

**Validation rules**:
- `type`: MUST be one of the 8 `EffectType` values.
- `intensity`: MUST be an integer in `[0, 100]` (inclusive). For `vintage`, the value is accepted but ignored by the pipeline.

---

### `EffectChain`

An ordered list of up to 5 effects to apply sequentially.

```typescript
export type EffectChain = EffectParam[]; // length: 0–5
```

**Validation rules**:
- Length MUST be 0–5 (inclusive). An empty chain is valid (no effects applied; output equals the original).
- Effects are applied left-to-right (index 0 first).

---

### `OutputFormat`

The supported output file formats for download and export.

```typescript
export type OutputFormat = 'jpeg' | 'png';
```

---

### `ProcessRequest`

The JSON body sent to `POST /api/photos/[id]/process` for single-photo download.

```typescript
export interface ProcessRequest {
  effects: EffectChain;
  format: OutputFormat;
}
```

---

### `ExportRequest`

The JSON body sent to `POST /api/photos/export` for a photo selection or `POST /api/albums/[id]/export` for a full album.

```typescript
export interface ExportRequest {
  effects: EffectChain; // applied uniformly to all photos
  format: OutputFormat;
  photoIds?: number[]; // required for /api/photos/export; ignored for /api/albums/[id]/export
}
```

**Validation rules**:
- `photoIds`: Required and non-empty when calling `/api/photos/export`. MUST NOT be present (or is ignored) when calling `/api/albums/[id]/export` (album ID comes from the URL).
- All other fields follow the same rules as `ProcessRequest`.

---

### `CssFilterString` (client-only, not in `types/index.ts`)

A derived string computed in the browser from an `EffectChain` for live preview. Not persisted or transmitted to the server.

```typescript
// Computed by a pure helper function in EffectsPanel.tsx
type CssFilterString = string; // e.g., "grayscale(1) blur(4px)"
```

**Derivation rules** (see research.md Decision 1 for the full mapping):

| Effect type | CSS token |
|-------------|-----------|
| `grayscale` | `grayscale({intensity/100})` |
| `sepia` | `sepia({intensity/100})` |
| `vintage` | `sepia(0.4) contrast(1.1) brightness(0.9) saturate(0.8)` |
| `blur` | `blur({intensity*0.08}px)` (min 0.3 px) |
| `sharpen` | `contrast(1.15) brightness(1.02)` |
| `brightness` | `brightness({0.5 + intensity*0.015})` |
| `contrast` | `contrast({0.5 + intensity*0.015})` |
| `saturation` | `saturate({intensity/33.3})` |

When the chain is empty, the filter string is `'none'`.

---

## Existing Entities — No Changes

The `Album` and `Photo` interfaces in `src/types/index.ts`, and the `albums` and `photos` SQLite tables in `src/lib/db/schema.ts`, are unchanged by this feature. The `photos.filepath` field is what `effect-service` reads to locate the source file for processing.

---

## Effect-to-Sharp Pipeline Rules

Derived from research.md Decision 2. Documented here for implementer reference.

| Effect type | Sharp operation(s) |
|-------------|-------------------|
| `grayscale` | `.grayscale()` |
| `sepia` | `.recomb([[0.393,0.769,0.189],[0.349,0.686,0.168],[0.272,0.534,0.131]])` |
| `vintage` | `.recomb(sepia_matrix).modulate({ brightness: 0.9, saturation: 0.8 }).linear(1.1, 0)` |
| `blur` | `.blur(Math.max(0.3, intensity * 0.08))` |
| `sharpen` | `.sharpen({ sigma: 1 + intensity * 0.03, m1: 1.5, m2: 0.7 })` |
| `brightness` | `.modulate({ brightness: 0.5 + intensity * 0.015 })` |
| `contrast` | `.linear(0.5 + intensity * 0.015, -(128 * (intensity * 0.015 - 0.5)))` |
| `saturation` | `.modulate({ saturation: intensity / 33.3 })` |

The pipeline is built by starting with `sharp(sourceBuffer)` and chaining each `EffectParam` in order. After all effects, the output is encoded using:
- `format === 'jpeg'` → `.jpeg({ quality: 90, progressive: true })`
- `format === 'png'` → `.png({ compressionLevel: 6 })`

The result is returned as a `Buffer` from `effect-service.applyEffects()`.
