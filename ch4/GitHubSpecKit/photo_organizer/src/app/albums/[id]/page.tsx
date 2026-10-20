'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import PhotoGrid from '@/components/PhotoGrid';
import LightboxOverlay from '@/components/LightboxOverlay';
import EmptyState from '@/components/EmptyState';
import ConfirmDialog from '@/components/ConfirmDialog';
import ExportDialog from '@/components/ExportDialog';
import type { Album, Photo } from '@/types';

export default function AlbumPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [album, setAlbum] = useState<Album | null>(null);
  const [photoList, setPhotoList] = useState<Photo[]>([]);
  const [loading, setLoading] = useState(true);
  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<number | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [selectMode, setSelectMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [exportScope, setExportScope] = useState<
    | { kind: 'album'; albumId: number }
    | { kind: 'selection'; photoIds: number[] }
    | null
  >(null);
  const scrollY = useRef(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchAlbum = useCallback(async () => {
    const res = await fetch(`/api/albums/${id}`);
    if (!res.ok) { router.push('/'); return; }
    const json = await res.json() as { album: Album; photos: Photo[] };
    setAlbum(json.album);
    setPhotoList(json.photos);
    setLoading(false);
  }, [id, router]);

  useEffect(() => { fetchAlbum(); }, [fetchAlbum]);

  const openLightbox = (index: number) => {
    if (selectMode) return;
    scrollY.current = window.scrollY;
    setLightboxIndex(index);
  };

  const closeLightbox = () => {
    setLightboxIndex(null);
    requestAnimationFrame(() => window.scrollTo(0, scrollY.current));
  };

  const handleUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setUploadError(null);
    setUploading(true);

    for (const file of Array.from(files)) {
      const form = new FormData();
      form.append('file', file);
      const res = await fetch(`/api/albums/${id}/photos`, { method: 'POST', body: form });
      const json = await res.json() as { photo?: Photo; message?: string };

      if (!res.ok) {
        setUploadError(json.message ?? 'Failed to upload photo.');
      } else if (json.photo) {
        setPhotoList((prev) => [...prev, json.photo!]);
      }
    }

    setUploading(false);
  };

  const handleDeleteConfirm = async () => {
    if (deleteTarget === null) return;
    await fetch(`/api/photos/${deleteTarget}`, { method: 'DELETE' });
    setPhotoList((prev) => prev.filter((p) => p.id !== deleteTarget));
    setDeleteTarget(null);
  };

  function toggleSelect(photoId: number) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(photoId)) next.delete(photoId);
      else next.add(photoId);
      return next;
    });
  }

  function exitSelectMode() {
    setSelectMode(false);
    setSelectedIds(new Set());
  }

  if (loading) return <div className="text-slate-500 text-sm">Loading album…</div>;
  if (!album) return null;

  const albumId = Number(id);

  return (
    <div>
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <button
          onClick={() => router.push('/')}
          className="text-slate-500 hover:text-slate-700"
          aria-label="Back to albums"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-slate-800">{album.name}</h2>
          <p className="text-sm text-slate-500">
            {album.date} · {photoList.length} {photoList.length === 1 ? 'photo' : 'photos'}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {uploading && <span className="text-sm text-slate-500">Uploading…</span>}

          {selectMode ? (
            <>
              <span className="text-sm text-slate-500">{selectedIds.size} selected</span>
              <button
                onClick={() => {
                  if (selectedIds.size === 0) return;
                  setExportScope({ kind: 'selection', photoIds: Array.from(selectedIds) });
                }}
                disabled={selectedIds.size === 0}
                aria-label="Export selected photos"
                className="px-3 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                Export Selected
              </button>
              <button
                onClick={exitSelectMode}
                className="px-3 py-2 text-sm font-medium text-slate-700 border border-slate-200 rounded-lg hover:bg-slate-50"
              >
                Cancel
              </button>
            </>
          ) : (
            <>
              {photoList.length > 0 && (
                <>
                  <button
                    data-testid="export-album"
                    onClick={() => setExportScope({ kind: 'album', albumId })}
                    aria-label="Export album"
                    className="px-3 py-2 text-sm font-medium text-slate-700 border border-slate-200 rounded-lg hover:bg-slate-50"
                  >
                    Export Album
                  </button>
                  <button
                    onClick={() => setSelectMode(true)}
                    aria-label="Select photos"
                    className="px-3 py-2 text-sm font-medium text-slate-700 border border-slate-200 rounded-lg hover:bg-slate-50"
                  >
                    Select
                  </button>
                </>
              )}
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                + Add Photos
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                multiple
                className="hidden"
                onChange={(e) => handleUpload(e.target.files)}
              />
            </>
          )}
        </div>
      </div>

      {uploadError && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          {uploadError}
          <button onClick={() => setUploadError(null)} className="ml-2 underline">Dismiss</button>
        </div>
      )}

      {photoList.length === 0 ? (
        <EmptyState
          title="No photos yet"
          description="Add photos to this album to get started."
          action={
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-5 py-2.5 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
            >
              Add Photos
            </button>
          }
        />
      ) : (
        <div>
          {selectMode && (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
              {photoList.map((photo) => (
                <button
                  key={photo.id}
                  data-testid="photo-tile"
                  onClick={() => toggleSelect(photo.id)}
                  aria-label={`Select ${photo.filename}`}
                  aria-pressed={selectedIds.has(photo.id)}
                  className={`relative aspect-square rounded-xl overflow-hidden border-2 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400
                    ${selectedIds.has(photo.id) ? 'border-blue-500' : 'border-transparent'}`}
                >
                  <img
                    src={photo.thumbnailUrl}
                    alt={photo.filename}
                    className="w-full h-full object-cover"
                  />
                  {selectedIds.has(photo.id) && (
                    <div className="absolute top-2 right-2 w-5 h-5 bg-blue-600 rounded-full flex items-center justify-center">
                      <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  )}
                </button>
              ))}
            </div>
          )}
          {!selectMode && (
            <PhotoGrid
              photos={photoList}
              onPhotoClick={openLightbox}
              onPhotoDelete={(photoId) => setDeleteTarget(photoId)}
            />
          )}
        </div>
      )}

      {lightboxIndex !== null && (
        <LightboxOverlay
          photos={photoList}
          currentIndex={lightboxIndex}
          onClose={closeLightbox}
          onNavigate={setLightboxIndex}
        />
      )}

      <ConfirmDialog
        isOpen={deleteTarget !== null}
        title="Remove Photo"
        message="Are you sure you want to remove this photo from the album?"
        confirmLabel="Remove"
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteTarget(null)}
      />

      {exportScope && (
        <ExportDialog
          scope={exportScope}
          onClose={() => setExportScope(null)}
        />
      )}
    </div>
  );
}
