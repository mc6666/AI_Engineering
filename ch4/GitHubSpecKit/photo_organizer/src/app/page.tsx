'use client';

import { useEffect, useState, useCallback } from 'react';
import AlbumGrid from '@/components/AlbumGrid';
import EmptyState from '@/components/EmptyState';
import CreateAlbumModal from '@/components/CreateAlbumModal';
import ConfirmDialog from '@/components/ConfirmDialog';
import type { Album } from '@/types';

function groupByYearMonth(albums: Album[]): Map<string, Album[]> {
  const map = new Map<string, Album[]>();
  for (const album of albums) {
    const key = album.date.slice(0, 7); // YYYY-MM
    if (!map.has(key)) map.set(key, []);
    map.get(key)!.push(album);
  }
  return map;
}

function formatYearMonth(key: string): string {
  const [year, month] = key.split('-');
  const date = new Date(Number(year), Number(month) - 1, 1);
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' });
}

export default function HomePage() {
  const [albums, setAlbums] = useState<Album[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Album | null>(null);

  const fetchAlbums = useCallback(async () => {
    const res = await fetch('/api/albums');
    const json = await res.json() as { albums: Album[] };
    setAlbums(json.albums);
    setLoading(false);
  }, []);

  useEffect(() => { fetchAlbums(); }, [fetchAlbums]);

  const handleCreated = (album: Album) => {
    setAlbums((prev) => [...prev, album]);
  };

  const handleDeleteRequest = (id: number) => {
    const target = albums.find((a) => a.id === id) ?? null;
    setDeleteTarget(target);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    await fetch(`/api/albums/${deleteTarget.id}`, { method: 'DELETE' });
    setAlbums((prev) => prev.filter((a) => a.id !== deleteTarget.id));
    setDeleteTarget(null);
  };

  if (loading) {
    return <div className="text-slate-500 text-sm">Loading albums…</div>;
  }

  const grouped = groupByYearMonth(albums);

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-2xl font-bold text-slate-800">Albums</h2>
        <button
          onClick={() => setShowCreate(true)}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
        >
          + Create Album
        </button>
      </div>

      {albums.length === 0 ? (
        <EmptyState
          title="No albums yet"
          description="Create your first album to start organizing your photos."
          action={
            <button
              onClick={() => setShowCreate(true)}
              className="px-5 py-2.5 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
            >
              Create Album
            </button>
          }
        />
      ) : (
        <div className="space-y-10">
          {[...grouped.entries()].map(([key, groupAlbums]) => (
            <section key={key}>
              <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4">
                {formatYearMonth(key)}
              </h3>
              <AlbumGrid initialAlbums={groupAlbums} onDelete={handleDeleteRequest} />
            </section>
          ))}
        </div>
      )}

      <CreateAlbumModal
        isOpen={showCreate}
        onClose={() => setShowCreate(false)}
        onCreated={handleCreated}
      />

      <ConfirmDialog
        isOpen={deleteTarget !== null}
        title="Delete Album"
        message={`Are you sure you want to delete "${deleteTarget?.name}"? This will permanently remove all photos in this album.`}
        confirmLabel="Delete"
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}
