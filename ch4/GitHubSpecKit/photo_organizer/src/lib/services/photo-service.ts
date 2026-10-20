import { eq, max, sql } from 'drizzle-orm';
import { photos, albums } from '@/lib/db/schema';
import { validateFile } from '@/lib/validation/file-validation';
import { setCoverPhoto } from '@/lib/services/album-service';
import type { Photo } from '@/types';
import type { createTestDb } from '@/lib/db/client';
import path from 'path';
import fs from 'fs';
import sharp from 'sharp';
import { randomUUID } from 'crypto';

type Db = ReturnType<typeof createTestDb>;

const DATA_DIR = process.env.DATA_DIR ?? './data';
const DEFAULT_ORDER_GAP = 1000;
const THUMBNAIL_SIZE = 400;

function toPhoto(row: typeof photos.$inferSelect): Photo {
  return {
    id: row.id,
    albumId: row.album_id,
    filename: row.filename,
    imageUrl: `/api/photos/${row.id}/image`,
    thumbnailUrl: `/api/photos/${row.id}/thumbnail`,
    mimeType: row.mime_type,
    sizeBytes: row.size_bytes,
    width: row.width ?? null,
    height: row.height ?? null,
    displayOrder: row.display_order,
    addedAt: row.added_at,
  };
}

export function getImagePath(db: Db, photoId: number, dataDir = DATA_DIR): string | null {
  const row = db.select().from(photos).where(eq(photos.id, photoId)).get();
  if (!row) return null;
  const resolved = path.resolve(path.join(dataDir, row.filepath));
  const base = path.resolve(dataDir);
  if (!resolved.startsWith(base)) return null; // path traversal guard
  return resolved;
}

export function getThumbnailPath(db: Db, photoId: number, dataDir = DATA_DIR): string | null {
  const row = db.select().from(photos).where(eq(photos.id, photoId)).get();
  if (!row) return null;
  const resolved = path.resolve(path.join(dataDir, row.thumbnail_path));
  const base = path.resolve(dataDir);
  if (!resolved.startsWith(base)) return null;
  return resolved;
}

export function getPhotoById(db: Db, photoId: number): Photo | null {
  const row = db.select().from(photos).where(eq(photos.id, photoId)).get();
  return row ? toPhoto(row) : null;
}

export async function addPhoto(
  db: Db,
  albumId: number,
  fileBuffer: Buffer,
  originalFilename: string,
  dataDir = DATA_DIR,
): Promise<Photo> {
  // Validate file type and size
  const header = fileBuffer.slice(0, 12);
  const mimeType = validateFile(header, fileBuffer.length);

  // Prepare extension
  const extMap: Record<string, string> = {
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/webp': '.webp',
    'image/gif': '.gif',
    'image/heic': '.heic',
    'image/heif': '.heif',
  };
  const ext = extMap[mimeType] ?? '.jpg';
  const uuid = randomUUID();

  // Create storage directories
  const photosDir = path.join(dataDir, 'photos', String(albumId));
  const thumbsDir = path.join(dataDir, 'thumbnails', String(albumId));
  fs.mkdirSync(photosDir, { recursive: true });
  fs.mkdirSync(thumbsDir, { recursive: true });

  const imageFilename = `${uuid}${ext}`;
  const thumbFilename = `${uuid}.jpg`;
  const imagePath = path.join(photosDir, imageFilename);
  const thumbPath = path.join(thumbsDir, thumbFilename);

  // Save original file
  fs.writeFileSync(imagePath, fileBuffer);

  // Generate thumbnail and extract metadata
  const sharpInstance = sharp(fileBuffer);
  const metadata = await sharpInstance.metadata();
  await sharp(fileBuffer)
    .resize(THUMBNAIL_SIZE, THUMBNAIL_SIZE, { fit: 'cover' })
    .jpeg({ quality: 80 })
    .toFile(thumbPath);

  // Relative paths stored in DB
  const relImagePath = path.join('photos', String(albumId), imageFilename);
  const relThumbPath = path.join('thumbnails', String(albumId), thumbFilename);

  // Assign display_order
  const maxRow = db.select({ m: max(photos.display_order) }).from(photos).where(eq(photos.album_id, albumId)).get();
  const displayOrder = (maxRow?.m ?? 0) + DEFAULT_ORDER_GAP;

  const inserted = db.insert(photos).values({
    album_id: albumId,
    filename: originalFilename,
    filepath: relImagePath,
    thumbnail_path: relThumbPath,
    mime_type: mimeType,
    size_bytes: fileBuffer.length,
    width: metadata.width ?? null,
    height: metadata.height ?? null,
    display_order: displayOrder,
  }).returning().get();

  // Set cover photo if this is the first photo in the album
  const countRow = db.select({ c: sql<number>`COUNT(*)` }).from(photos).where(eq(photos.album_id, albumId)).get();
  if ((countRow?.c ?? 0) === 1) {
    setCoverPhoto(db, albumId, inserted.id);
  }

  return toPhoto(inserted);
}

export function removePhoto(
  db: Db,
  photoId: number,
  dataDir = DATA_DIR,
): boolean {
  const row = db.select().from(photos).where(eq(photos.id, photoId)).get();
  if (!row) return false;

  // Delete files
  safeUnlink(path.join(dataDir, row.filepath));
  safeUnlink(path.join(dataDir, row.thumbnail_path));

  // Delete DB row
  db.delete(photos).where(eq(photos.id, photoId)).run();

  // Update album cover if this was the cover photo
  const albumRow = db.select().from(albums).where(eq(albums.id, row.album_id)).get();
  if (albumRow?.cover_photo_id === photoId) {
    const nextPhoto = db.select().from(photos).where(eq(photos.album_id, row.album_id)).get();
    setCoverPhoto(db, row.album_id, nextPhoto?.id ?? null);
  }

  return true;
}

function safeUnlink(filePath: string): void {
  try { fs.unlinkSync(filePath); } catch { /* ignore if missing */ }
}
