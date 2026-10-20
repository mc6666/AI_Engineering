'use client';

import { useState } from 'react';
import type { EffectType, EffectChain, OutputFormat } from '@/types';

const EFFECTS: Array<{ type: EffectType; label: string }> = [
  { type: 'grayscale', label: 'Grayscale' },
  { type: 'sepia', label: 'Sepia' },
  { type: 'vintage', label: 'Vintage' },
  { type: 'blur', label: 'Blur' },
  { type: 'sharpen', label: 'Sharpen' },
  { type: 'brightness', label: 'Brightness' },
  { type: 'contrast', label: 'Contrast' },
  { type: 'saturation', label: 'Saturation' },
];

type ExportScope =
  | { kind: 'album'; albumId: number }
  | { kind: 'selection'; photoIds: number[] };

interface ExportDialogProps {
  scope: ExportScope;
  onClose: () => void;
}

export default function ExportDialog({ scope, onClose }: ExportDialogProps) {
  const [selectedEffect, setSelectedEffect] = useState<EffectType | null>(null);
  const [intensity, setIntensity] = useState(100);
  const [format, setFormat] = useState<OutputFormat>('jpeg');
  const [progress, setProgress] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [controller, setController] = useState<AbortController | null>(null);

  const chain: EffectChain = selectedEffect
    ? [{ type: selectedEffect, intensity }]
    : [];

  async function handleExport() {
    setError(null);
    setProgress('Preparing export…');
    const ctrl = new AbortController();
    setController(ctrl);

    try {
      let url: string;
      let filename: string;
      let body: object;

      if (scope.kind === 'album') {
        url = `/api/albums/${scope.albumId}/export`;
        filename = `album-${scope.albumId}-export.zip`;
        body = { effects: chain, format };
      } else {
        url = '/api/photos/export';
        filename = 'photos-export.zip';
        body = { effects: chain, format, photoIds: scope.photoIds };
      }

      setProgress('Downloading…');
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: ctrl.signal,
      });

      if (!res.ok) {
        const err = await res.json() as { message?: string };
        throw new Error(err.message ?? 'Export failed');
      }

      const blob = await res.blob();
      const objUrl = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = objUrl;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(objUrl);

      setProgress(null);
      onClose();
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        setError((err as Error).message);
        setProgress(null);
      } else {
        setProgress(null);
      }
    } finally {
      setController(null);
    }
  }

  function handleCancel() {
    controller?.abort();
    setProgress(null);
    setError(null);
  }

  const photoCount =
    scope.kind === 'album' ? 'all photos' : `${scope.photoIds.length} photo${scope.photoIds.length === 1 ? '' : 's'}`;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
      role="dialog"
      aria-modal="true"
      aria-label="Export photos"
    >
      <div
        className="bg-white rounded-2xl shadow-xl p-6 w-80 flex flex-col gap-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800">Export {photoCount}</h2>
          <button
            onClick={onClose}
            aria-label="Close export dialog"
            className="text-slate-400 hover:text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-400 rounded"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Format selector */}
        <div className="flex items-center gap-3">
          <label htmlFor="export-format" className="text-sm text-slate-600 shrink-0">Format</label>
          <select
            id="export-format"
            value={format}
            onChange={(e) => setFormat(e.target.value as OutputFormat)}
            className="flex-1 border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <option value="jpeg">JPEG</option>
            <option value="png">PNG</option>
          </select>
        </div>

        {/* Uniform effect picker */}
        <div>
          <p className="text-sm text-slate-600 mb-2">Apply effect (optional)</p>
          <div className="grid grid-cols-2 gap-2">
            {EFFECTS.map(({ type, label }) => (
              <button
                key={type}
                onClick={() => setSelectedEffect(selectedEffect === type ? null : type)}
                aria-pressed={selectedEffect === type}
                aria-label={label}
                className={`p-2 rounded-lg text-xs font-medium border transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400
                  ${selectedEffect === type
                    ? 'bg-blue-600 border-blue-400 text-white'
                    : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                  }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Intensity slider */}
        {selectedEffect && (
          <div className="flex flex-col gap-1">
            <label htmlFor="export-intensity" className="text-xs text-slate-500">
              {selectedEffect} intensity: {intensity}%
            </label>
            <input
              id="export-intensity"
              type="range"
              min={0}
              max={100}
              value={intensity}
              onChange={(e) => setIntensity(Number(e.target.value))}
              aria-label={`${selectedEffect} intensity`}
              className="w-full accent-blue-500"
            />
          </div>
        )}

        {error && <p className="text-sm text-red-600">{error}</p>}
        {progress && <p className="text-sm text-slate-500">{progress}</p>}

        <div className="flex gap-2 justify-end pt-1">
          {progress ? (
            <button
              onClick={handleCancel}
              className="px-4 py-2 text-sm font-medium text-slate-700 border border-slate-200 rounded-lg hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-400"
            >
              Cancel
            </button>
          ) : (
            <>
              <button
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-slate-700 border border-slate-200 rounded-lg hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-400"
              >
                Cancel
              </button>
              <button
                data-testid="export-confirm"
                onClick={handleExport}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
              >
                Export
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
