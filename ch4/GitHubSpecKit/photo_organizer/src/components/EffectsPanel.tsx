'use client';

import { useState } from 'react';
import type { EffectChain, EffectParam, EffectType, OutputFormat } from '@/types';

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

interface EffectsPanelProps {
  photoId: number;
  chain: EffectChain;
  onChainChange: (chain: EffectChain) => void;
}

export default function EffectsPanel({ photoId, chain, onChainChange }: EffectsPanelProps) {
  const [selectedType, setSelectedType] = useState<EffectType | null>(
    chain.length > 0 ? chain[chain.length - 1].type : null,
  );
  const [intensity, setIntensity] = useState<number>(
    chain.length > 0 ? chain[chain.length - 1].intensity : 100,
  );
  const [format, setFormat] = useState<OutputFormat>('jpeg');
  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  function selectEffect(type: EffectType) {
    setSelectedType(type);
    const existing = chain.find((e) => e.type === type);
    const newIntensity = existing?.intensity ?? intensity;
    setIntensity(newIntensity);

    const withoutType = chain.filter((e) => e.type !== type);
    const updated: EffectChain = [...withoutType, { type, intensity: newIntensity }];
    onChainChange(updated.slice(-5));
  }

  function updateIntensity(value: number) {
    setIntensity(value);
    if (!selectedType) return;
    const updated: EffectChain = chain.map((e) =>
      e.type === selectedType ? { ...e, intensity: value } : e,
    );
    onChainChange(updated);
  }

  function reset() {
    setSelectedType(null);
    setIntensity(100);
    onChainChange([]);
  }

  async function handleDownload() {
    setDownloadError(null);
    setDownloading(true);
    const controller = new AbortController();

    try {
      const res = await fetch(`/api/photos/${photoId}/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ effects: chain, format } satisfies { effects: EffectChain; format: OutputFormat }),
        signal: controller.signal,
      });

      if (!res.ok) {
        const err = await res.json() as { message?: string };
        throw new Error(err.message ?? 'Download failed');
      }

      const blob = await res.blob();
      const ext = format === 'png' ? 'png' : 'jpg';
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `photo-${photoId}-processed.${ext}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        setDownloadError((err as Error).message);
      }
    } finally {
      setDownloading(false);
    }
  }

  const currentEffect = selectedType
    ? chain.find((e: EffectParam) => e.type === selectedType)
    : null;

  return (
    <div
      data-testid="effects-panel"
      className="flex flex-col gap-4 bg-black/80 p-4 rounded-xl w-64 text-white"
    >
      <div className="grid grid-cols-2 gap-2" role="group" aria-label="Effect tiles">
        {EFFECTS.map(({ type, label }) => {
          const isSelected = chain.some((e: EffectParam) => e.type === type);
          return (
            <button
              key={type}
              data-testid="effect-tile"
              data-effect={type}
              aria-label={label}
              aria-pressed={isSelected}
              onClick={() => selectEffect(type)}
              className={`p-2 rounded-lg text-xs font-medium border transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400
                ${isSelected
                  ? 'bg-blue-600 border-blue-400 text-white'
                  : 'bg-white/10 border-white/20 text-white/80 hover:bg-white/20'
                }`}
            >
              {label}
            </button>
          );
        })}
      </div>

      {selectedType && (
        <div className="flex flex-col gap-1">
          <label
            htmlFor="intensity-slider"
            className="text-xs text-white/60"
          >
            Intensity: {currentEffect?.intensity ?? intensity}%
          </label>
          <input
            id="intensity-slider"
            data-testid="intensity-slider"
            type="range"
            min={0}
            max={100}
            value={currentEffect?.intensity ?? intensity}
            onChange={(e) => updateIntensity(Number(e.target.value))}
            aria-label={`${selectedType} intensity`}
            className="w-full accent-blue-500"
          />
        </div>
      )}

      <button
        data-testid="reset-effects"
        onClick={reset}
        aria-label="Reset all effects"
        className="text-xs text-white/60 hover:text-white underline text-left focus:outline-none focus:ring-2 focus:ring-blue-400 rounded"
      >
        Reset
      </button>

      <div className="border-t border-white/20 pt-3 flex flex-col gap-2">
        <div className="flex gap-2 items-center">
          <label htmlFor="format-select" className="text-xs text-white/60 shrink-0">Format</label>
          <select
            id="format-select"
            value={format}
            onChange={(e) => setFormat(e.target.value as OutputFormat)}
            className="flex-1 bg-white/10 text-white text-xs rounded px-2 py-1 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <option value="jpeg">JPEG</option>
            <option value="png">PNG</option>
          </select>
        </div>

        {downloadError && (
          <p className="text-xs text-red-400">{downloadError}</p>
        )}

        <button
          data-testid="download-photo"
          onClick={handleDownload}
          disabled={downloading}
          aria-label="Download processed photo"
          className="px-3 py-2 text-xs font-medium bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          {downloading ? 'Processing…' : 'Download'}
        </button>
      </div>
    </div>
  );
}
