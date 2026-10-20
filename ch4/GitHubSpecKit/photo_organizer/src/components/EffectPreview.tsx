'use client';

import type { EffectChain, EffectParam } from '@/types';

export function deriveCssFilter(chain: EffectChain): string {
  if (chain.length === 0) return 'none';

  const tokens: string[] = [];
  for (const { type, intensity } of chain) {
    switch (type) {
      case 'grayscale':
        tokens.push(`grayscale(${intensity / 100})`);
        break;
      case 'sepia':
        tokens.push(`sepia(${intensity / 100})`);
        break;
      case 'vintage':
        tokens.push('sepia(0.4) contrast(1.1) brightness(0.9) saturate(0.8)');
        break;
      case 'blur':
        tokens.push(`blur(${Math.max(0.3, intensity * 0.08).toFixed(2)}px)`);
        break;
      case 'sharpen':
        tokens.push('contrast(1.15) brightness(1.02)');
        break;
      case 'brightness':
        tokens.push(`brightness(${(0.5 + intensity * 0.015).toFixed(3)})`);
        break;
      case 'contrast':
        tokens.push(`contrast(${(0.5 + intensity * 0.015).toFixed(3)})`);
        break;
      case 'saturation':
        tokens.push(`saturate(${(intensity / 33.3).toFixed(3)})`);
        break;
    }
  }
  return tokens.join(' ') || 'none';
}

interface EffectPreviewProps {
  src: string;
  alt: string;
  chain: EffectChain;
  className?: string;
}

export default function EffectPreview({ src, alt, chain, className = '' }: EffectPreviewProps) {
  const filter = deriveCssFilter(chain);
  return (
    <img
      src={src}
      alt={alt}
      data-testid="effect-preview-img"
      className={`max-h-screen max-w-full object-contain ${className}`}
      style={{ filter: filter === 'none' ? undefined : filter }}
    />
  );
}
