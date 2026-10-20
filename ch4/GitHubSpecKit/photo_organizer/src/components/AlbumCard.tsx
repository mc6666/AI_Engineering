'use client';

import Link from 'next/link';
import type { Album } from '@/types';

interface AlbumCardProps {
  album: Album;
  onDelete?: (id: number) => void;
  dragHandleProps?: Record<string, unknown>;
  style?: React.CSSProperties;
}

export default function AlbumCard({ album, onDelete, dragHandleProps, style }: AlbumCardProps) {
  return (
    <div
      style={style}
      className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow group"
    >
      {/* Cover image */}
      <div className="relative aspect-video bg-slate-100 overflow-hidden">
        {album.coverThumbnailUrl ? (
          <img
            src={album.coverThumbnailUrl}
            alt={`Cover of ${album.name}`}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="flex items-center justify-center h-full text-slate-300">
            <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}

        {/* Drag handle */}
        {dragHandleProps && (
          <button
            {...dragHandleProps}
            aria-label="Drag to reorder"
            className="absolute top-2 left-2 p-1 rounded bg-white/80 opacity-0 group-hover:opacity-100 transition-opacity cursor-grab active:cursor-grabbing"
          >
            <svg className="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8h16M4 16h16" />
            </svg>
          </button>
        )}
      </div>

      {/* Card footer */}
      <div className="p-3 flex items-start justify-between gap-2">
        <Link href={`/albums/${album.id}`} className="min-w-0 flex-1 hover:text-blue-600">
          <p className="font-medium text-slate-800 truncate">{album.name}</p>
          <p className="text-xs text-slate-500 mt-0.5">
            {album.date} · {album.photoCount} {album.photoCount === 1 ? 'photo' : 'photos'}
          </p>
        </Link>

        {onDelete && (
          <button
            onClick={() => onDelete(album.id)}
            aria-label={`Delete album ${album.name}`}
            className="flex-shrink-0 p-1.5 rounded text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
