'use client';

import { useEffect, useCallback, useState } from 'react';
import type { Photo } from '@/types';
import type { EffectChain } from '@/types';
import EffectsPanel from '@/components/EffectsPanel';
import EffectPreview from '@/components/EffectPreview';

interface LightboxOverlayProps {
  photos: Photo[];
  currentIndex: number;
  onClose: () => void;
  onNavigate: (index: number) => void;
}

export default function LightboxOverlay({
  photos,
  currentIndex,
  onClose,
  onNavigate,
}: LightboxOverlayProps) {
  const photo = photos[currentIndex];
  const hasPrev = currentIndex > 0;
  const hasNext = currentIndex < photos.length - 1;
  const [showEffects, setShowEffects] = useState(false);
  const [effectChain, setEffectChain] = useState<EffectChain>([]);

  const handleKey = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape') onClose();
    if (e.key === 'ArrowLeft' && hasPrev) onNavigate(currentIndex - 1);
    if (e.key === 'ArrowRight' && hasNext) onNavigate(currentIndex + 1);
  }, [onClose, onNavigate, currentIndex, hasPrev, hasNext]);

  useEffect(() => {
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [handleKey]);

  // Reset effects when navigating to a different photo
  useEffect(() => {
    setEffectChain([]);
    setShowEffects(false);
  }, [currentIndex]);

  if (!photo) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/90"
      role="dialog"
      aria-modal="true"
      aria-label={`Photo ${currentIndex + 1} of ${photos.length}: ${photo.filename}`}
    >
      {/* Backdrop click to close */}
      <div className="absolute inset-0" onClick={onClose} aria-hidden="true" />

      {/* Close button */}
      <button
        onClick={onClose}
        aria-label="Close lightbox"
        className="absolute top-4 right-4 p-2 text-white/70 hover:text-white z-10"
      >
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      {/* Effects toggle */}
      <button
        data-testid="effects-toggle"
        onClick={(e) => { e.stopPropagation(); setShowEffects((v) => !v); }}
        aria-label="Toggle effects panel"
        aria-expanded={showEffects}
        className="absolute top-4 left-4 p-2 text-white/70 hover:text-white z-10 flex items-center gap-1 text-sm"
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M12 3v1m0 16v1m8.66-13l-.87.5M4.21 17.5l-.87.5M20.66 17.5l-.87-.5M4.21 6.5l-.87-.5M21 12h-1M4 12H3" />
        </svg>
        Effects
      </button>

      {/* Previous */}
      {hasPrev && (
        <button
          onClick={() => onNavigate(currentIndex - 1)}
          aria-label="Previous photo"
          className="absolute left-4 top-1/2 -translate-y-1/2 p-3 text-white/70 hover:text-white z-10"
        >
          <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
      )}

      {/* Image */}
      <div className="relative z-0 flex items-center justify-center" onClick={(e) => e.stopPropagation()}>
        <EffectPreview
          src={photo.imageUrl}
          alt={photo.filename}
          chain={effectChain}
        />
      </div>

      {/* Next */}
      {hasNext && (
        <button
          onClick={() => onNavigate(currentIndex + 1)}
          aria-label="Next photo"
          className="absolute right-4 top-1/2 -translate-y-1/2 p-3 text-white/70 hover:text-white z-10"
        >
          <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      )}

      {/* Effects panel (right side) */}
      {showEffects && (
        <div
          className="absolute right-4 top-1/2 -translate-y-1/2 z-10"
          onClick={(e) => e.stopPropagation()}
        >
          <EffectsPanel
            photoId={photo.id}
            chain={effectChain}
            onChainChange={setEffectChain}
          />
        </div>
      )}

      {/* Counter */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-white/60 text-sm">
        {currentIndex + 1} / {photos.length}
      </div>
    </div>
  );
}
