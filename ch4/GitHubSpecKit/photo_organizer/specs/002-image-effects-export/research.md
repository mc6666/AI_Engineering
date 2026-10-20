# Research: Image Processing with Special Effects & Export

**Feature**: Image Effects & Export
**Date**: 2026-06-17

---

## Decision 1: Live Preview Strategy

**Decision**: Use browser-native CSS `filter` property for live preview; apply `sharp` server-side only at download/export time.

**Rationale**: CSS filters run entirely in the GPU compositor — zero server round-trips, sub-16 ms update latency on any modern machine. All eight effects in the curated set (grayscale, sepia, vintage, blur, sharpen, brightness, contrast, saturation) have CSS equivalents that are visually close enough for a preview. `sharp` is used at download/export time for pixel-accurate, high-quality output that matches the preview intent.

**Alternatives considered**:
- Server-side preview (call API on every slider change): Rejected — network latency (≥ 100 ms) makes it unusable for real-time sliders; adds server load for a transient operation.
- Canvas-based preview (Web Workers + WASM): Rejected — adds significant bundle complexity; CSS filters are sufficient for this effect set with no perceptual loss.

**CSS filter → intent mapping**:

| Effect | CSS `filter` string (preview) | Note |
|--------|-------------------------------|------|
| grayscale | `grayscale(1)` | Full grey at intensity 100 |
| sepia | `sepia(1)` | Full sepia at intensity 100 |
| vintage | `sepia(0.4) contrast(1.1) brightness(0.9) saturate(0.8)` | Fixed preset, no intensity param |
| blur | `blur({N}px)` | N = intensity mapped 0–8 |
| sharpen | `contrast(1.15) brightness(1.02)` | CSS has no sharpen; contrast is a close visual proxy |
| brightness | `brightness({V})` | V mapped 0.5–2.0 from intensity 0–100 |
| contrast | `contrast({V})` | V mapped 0.5–2.0 from intensity 0–100 |
| saturation | `saturate({V})` | V mapped 0–3.0 from intensity 0–100 |

---

## Decision 2: Server-Side Effect Pipeline (`sharp`)

**Decision**: Build a composable `sharp` pipeline from `EffectParam[]` in `effect-service.ts`. Each effect type maps to one or more chained `sharp` operations.

**Rationale**: `sharp` (libvips) is already installed and used for thumbnail generation. It handles all required operations natively. Chaining is idiomatic to sharp's fluent API. No additional binary dependency is required.

**Sharp operation mapping**:

| Effect | Sharp chain |
|--------|-------------|
| `grayscale` | `.grayscale()` |
| `sepia` | `.recomb([[0.393,0.769,0.189],[0.349,0.686,0.168],[0.272,0.534,0.131]])` — standard sepia matrix |
| `vintage` | `.recomb(sepia_matrix).modulate({ brightness: 0.9, saturation: 0.8 }).linear(1.1, 0)` |
| `blur` | `.blur(sigma)` where sigma = max(0.3, intensity * 0.08) (0.3 = sharp minimum) |
| `sharpen` | `.sharpen({ sigma: 1 + intensity * 0.03, m1: 1.5, m2: 0.7 })` |
| `brightness` | `.modulate({ brightness: 0.5 + intensity * 0.015 })` |
| `contrast` | `.linear(0.5 + intensity * 0.015, -(128 * (intensity * 0.015 - 0.5)))` |
| `saturation` | `.modulate({ saturation: intensity / 33.3 })` |

Effects in the chain are applied in order (index 0 first). Maximum chain depth: 5.

**Output format mapping**:
- `jpeg` → `.jpeg({ quality: 90, progressive: true })`
- `png` → `.png({ compressionLevel: 6 })`

---

## Decision 3: ZIP Creation for Batch Export

**Decision**: Use `archiver` ^7 with the `zip` format and a `PassThrough` stream to pipe the ZIP directly into the HTTP response without writing to disk.

**Rationale**: `archiver` is the de-facto Node.js library for streaming ZIP creation (10M+ weekly downloads, well-maintained, streams-native API). It pipes entries from `Buffer` or `Readable` sources, making it straightforward to add processed image buffers as they are generated. No temp files needed.

**Alternatives considered**:
- `jszip`: Rejected — accumulates the entire archive in memory before outputting; unsuitable for large albums (memory spike).
- Native `zlib` + manual ZIP format: Rejected — significant implementation complexity for no gain over `archiver`.
- Writing ZIP to disk first: Rejected — requires temp-file cleanup, adds disk I/O latency, and is excluded by spec constraint (ephemeral processing only).

**Stream architecture**:
```
archiver('zip') → PassThrough → Response (ReadableStream)
  ↑
  photo_1 buffer → effect-service.applyEffects() → archiver.append()
  photo_2 buffer → effect-service.applyEffects() → archiver.append()
  ...
  archiver.finalize()
```

Photos are processed and appended sequentially to avoid memory spikes.

---

## Decision 4: Single Photo Download — API Response

**Decision**: `POST /api/photos/[id]/process` processes the photo with `sharp` and returns the binary result directly via a `Response` with `Content-Disposition: attachment`.

**Rationale**: Next.js 15 App Router API routes return standard `Response` objects. Returning a binary buffer as the response body with the correct `Content-Type` and `Content-Disposition` headers triggers a browser download without any client-side Blob URL manipulation. This is the simplest correct approach.

**Response headers**:
- `Content-Type: image/jpeg` or `image/png`
- `Content-Disposition: attachment; filename="photo-{id}-processed.jpg"`
- `Cache-Control: no-store` (processed output is not cacheable; depends on request body)

---

## Decision 5: Effect Chain Transmission — Request Body

**Decision**: The effect chain is passed as a JSON request body to all processing endpoints. No URL query params; no session storage.

**Rationale**: Effect chains can contain up to 5 objects with floating-point intensity values, which exceeds safe query-string length and encoding. POST body is idiomatic for parametric server actions. No state storage needed — the chain is fully described by the request.

**Request body shape** (all endpoints):
```json
{
  "effects": [
    { "type": "grayscale", "intensity": 100 },
    { "type": "blur", "intensity": 40 }
  ],
  "format": "jpeg"
}
```

Validation: `effects` array length must be 0–5; each `type` must be one of the 8 known values; `intensity` must be 0–100 (integer); `format` must be `"jpeg"` or `"png"`.

---

## Decision 6: Cancellation Strategy

**Decision**: Batch export cancellation is handled client-side by aborting the fetch using `AbortController`. The server does not need a separate cancel endpoint.

**Rationale**: The export is a single streaming HTTP response. Closing the connection (via `AbortController.abort()`) causes the server-side `Request` to be aborted, and `archiver` will stop writing. The browser disposes any partially received response. No partial file is ever saved since the browser only presents the download dialog after the complete response is received (or in streaming mode, after the connection closes normally). The 2-second cleanup SLA is satisfied inherently — abort is synchronous.

**Alternative considered**: Server-side cancel endpoint with job tracking (store job ID in memory, call DELETE /api/export/{jobId}). Rejected — adds stateful job management complexity for a single-user local app with no concurrent exports.
