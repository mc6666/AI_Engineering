'use client';

interface PhotoTileProps {
  thumbnailUrl: string;
  filename: string;
  onClick: () => void;
  onDelete?: () => void;
}

export default function PhotoTile({ thumbnailUrl, filename, onClick, onDelete }: PhotoTileProps) {
  return (
    <div className="relative group aspect-square bg-slate-100 rounded-lg overflow-hidden cursor-pointer">
      <img
        src={thumbnailUrl}
        alt={filename}
        loading="lazy"
        onClick={onClick}
        className="w-full h-full object-cover transition-transform group-hover:scale-105"
      />

      {/* Hover overlay */}
      <div
        onClick={onClick}
        className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors"
        aria-hidden="true"
      />

      {onDelete && (
        <button
          onClick={(e) => { e.stopPropagation(); onDelete(); }}
          aria-label={`Remove photo ${filename}`}
          className="absolute top-1.5 right-1.5 p-1 rounded bg-white/90 opacity-0 group-hover:opacity-100 transition-opacity text-red-500 hover:text-red-700"
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  );
}
