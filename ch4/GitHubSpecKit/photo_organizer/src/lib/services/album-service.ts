import { eq, asc, max, sql } from 'drizzle-orm';
import { albums, photos } from '@/lib/db/schema';
import type { Album, AlbumWithPhotos } from '@/types';
import type { createTestDb } from '@/lib/db/client';
import path from 'path';
import fs from 'fs';

type Db = ReturnType<typeof createTestDb>;

const DEFAULT_ORDER_GAP = 1000;
const RENORM_THRESHOLD = 0.001;

function toAlbum(row: typeof albums.$inferSelect, photoCount = 0): Album {
  return {
    id: row.id,
    name: row.name,
    date: row.date,
    displayOrder: row.display_order,
    coverPhotoId: row.cover_photo_id ?? null,
    coverThumbnailUrl: row.cover_photo_id ? `/api/photos/${row.cover_photo_id}/thumbnail` : null,
    photoCount,
    createdAt: row.created_at,
  };
}

export async function getAllAlbums(db: Db): Promise<Album[]> {
  const rows = db
    .select({
      album: albums,
      photoCount: sql<number>`COUNT(${photos.id})`.as('photo_count'),
    })
    .from(albums)
    .leftJoin(photos, eq(photos.album_id, albums.id))
    .groupBy(albums.id)
    .orderBy(asc(albums.display_order))
    .all();

  return rows.map((r) => toAlbum(r.album, r.photoCount));
}

export async function getAlbumById(db: Db, id: number): Promise<AlbumWithPhotos | null> {
  const albumRow = db.select().from(albums).where(eq(albums.id, id)).get();
  if (!albumRow) return null;

  const photoRows = db
    .select()
    .from(photos)
    .where(eq(photos.album_id, id))
    .orderBy(asc(photos.display_order))
    .all();

  const photoList = photoRows.map((p) => ({
    id: p.id,
    albumId: p.album_id,
    filename: p.filename,
    imageUrl: `/api/photos/${p.id}/image`,
    thumbnailUrl: `/api/photos/${p.id}/thumbnail`,
    mimeType: p.mime_type,
    sizeBytes: p.size_bytes,
    width: p.width ?? null,
    height: p.height ?? null,
    displayOrder: p.display_order,
    addedAt: p.added_at,
  }));

  return { ...toAlbum(albumRow, photoList.length), photos: photoList };
}

export async function createAlbum(db: Db, data: { name: string; date: string }): Promise<Album> {
  const maxRow = db.select({ m: max(albums.display_order) }).from(albums).get();
  const nextOrder = (maxRow?.m ?? 0) + DEFAULT_ORDER_GAP;

  const result = db
    .insert(albums)
    .values({ name: data.name, date: data.date, display_order: nextOrder })
    .returning()
    .get();

  return toAlbum(result, 0);
}

export async function updateAlbum(
  db: Db,
  id: number,
  data: Partial<{ name: string; date: string }>,
): Promise<Album | null> {
  const existing = db.select().from(albums).where(eq(albums.id, id)).get();
  if (!existing) return null;

  const updated = db
    .update(albums)
    .set(data)
    .where(eq(albums.id, id))
    .returning()
    .get();

  const countRow = db
    .select({ c: sql<number>`COUNT(*)` })
    .from(photos)
    .where(eq(photos.album_id, id))
    .get();

  return toAlbum(updated, countRow?.c ?? 0);
}

export async function deleteAlbum(db: Db, id: number, dataDir: string): Promise<boolean> {
  const existing = db.select().from(albums).where(eq(albums.id, id)).get();
  if (!existing) return false;

  // Remove photo files from disk (cascade in DB handles rows)
  const photosToDelete = db.select().from(photos).where(eq(photos.album_id, id)).all();
  for (const p of photosToDelete) {
    safeUnlink(path.join(dataDir, p.filepath));
    safeUnlink(path.join(dataDir, p.thumbnail_path));
  }

  db.delete(albums).where(eq(albums.id, id)).run();

  // Clean up album directories
  safeRmdir(path.join(dataDir, 'photos', String(id)));
  safeRmdir(path.join(dataDir, 'thumbnails', String(id)));

  return true;
}

export async function reorderAlbum(
  db: Db,
  id: number,
  opts: { predecessorOrder?: number; successorOrder?: number },
): Promise<Album> {
  let newOrder: number;

  if (opts.predecessorOrder !== undefined && opts.successorOrder !== undefined) {
    newOrder = (opts.predecessorOrder + opts.successorOrder) / 2;
  } else if (opts.predecessorOrder !== undefined) {
    newOrder = opts.predecessorOrder + DEFAULT_ORDER_GAP;
  } else if (opts.successorOrder !== undefined) {
    newOrder = opts.successorOrder / 2;
  } else {
    throw new Error('At least one of predecessorOrder or successorOrder must be provided');
  }

  db.update(albums).set({ display_order: newOrder }).where(eq(albums.id, id)).run();

  // Check if renormalization is needed
  if (opts.predecessorOrder !== undefined && opts.successorOrder !== undefined) {
    const gap = Math.abs((opts.successorOrder - opts.predecessorOrder) / 2);
    if (gap < RENORM_THRESHOLD) {
      renormalizeOrders(db);
    }
  }

  const updated = db.select().from(albums).where(eq(albums.id, id)).get()!;
  const countRow = db
    .select({ c: sql<number>`COUNT(*)` })
    .from(photos)
    .where(eq(photos.album_id, id))
    .get();

  return toAlbum(updated, countRow?.c ?? 0);
}

function renormalizeOrders(db: Db): void {
  const allAlbums = db.select().from(albums).orderBy(asc(albums.display_order)).all();
  db.transaction((tx) => {
    allAlbums.forEach((a, i) => {
      tx.update(albums)
        .set({ display_order: (i + 1) * DEFAULT_ORDER_GAP })
        .where(eq(albums.id, a.id))
        .run();
    });
  });
}

export function setCoverPhoto(db: Db, albumId: number, photoId: number | null): void {
  db.update(albums).set({ cover_photo_id: photoId }).where(eq(albums.id, albumId)).run();
}

function safeUnlink(filePath: string): void {
  try { fs.unlinkSync(filePath); } catch { /* ignore if missing */ }
}

function safeRmdir(dirPath: string): void {
  try { fs.rmdirSync(dirPath); } catch { /* ignore if not empty or missing */ }
}
