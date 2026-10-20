import path from 'path';
import fs from 'fs';
import sharp from 'sharp';
import { createTestDb, closeDb } from '@/lib/db/client';
import { createAlbum } from '@/lib/services/album-service';
import { addPhoto, removePhoto, getImagePath, getThumbnailPath } from '@/lib/services/photo-service';

const TEST_DB = path.join(__dirname, '../../../data/test-photo-service.db');
const TEST_DATA = path.join(__dirname, '../../../data/test-photo-data');
const FIXTURES = path.join(__dirname, '../../fixtures/images');

let db: ReturnType<typeof createTestDb>;
let sampleJpgBuffer: Buffer;

beforeAll(async () => {
  fs.mkdirSync(path.dirname(TEST_DB), { recursive: true });
  fs.mkdirSync(TEST_DATA, { recursive: true });
  fs.mkdirSync(FIXTURES, { recursive: true });

  if (fs.existsSync(TEST_DB)) fs.unlinkSync(TEST_DB);
  db = createTestDb(TEST_DB);

  // Generate sample image buffer
  sampleJpgBuffer = await sharp({
    create: { width: 50, height: 50, channels: 3, background: { r: 200, g: 100, b: 50 } },
  }).jpeg({ quality: 80 }).toBuffer();
});

afterAll(() => {
  closeDb(db);
  if (fs.existsSync(TEST_DB)) fs.unlinkSync(TEST_DB);
  fs.rmSync(TEST_DATA, { recursive: true, force: true });
});

describe('addPhoto', () => {
  it('saves original file and thumbnail to disk', async () => {
    const album = await createAlbum(db, { name: 'Test Album', date: '2026-06-01' });
    const photo = await addPhoto(db, album.id, sampleJpgBuffer, 'test.jpg', TEST_DATA);

    expect(photo.mimeType).toBe('image/jpeg');
    expect(photo.sizeBytes).toBe(sampleJpgBuffer.length);
    expect(photo.width).toBeGreaterThan(0);

    const imagePath = getImagePath(db, photo.id, TEST_DATA);
    const thumbPath = getThumbnailPath(db, photo.id, TEST_DATA);
    expect(imagePath).not.toBeNull();
    expect(thumbPath).not.toBeNull();
    expect(fs.existsSync(imagePath!)).toBe(true);
    expect(fs.existsSync(thumbPath!)).toBe(true);
  });

  it('sets album cover_photo_id for first photo', async () => {
    const { albums } = await import('@/lib/db/schema');
    const { eq } = await import('drizzle-orm');
    const album = await createAlbum(db, { name: 'Cover Test', date: '2026-06-02' });
    const photo = await addPhoto(db, album.id, sampleJpgBuffer, 'first.jpg', TEST_DATA);

    const albumRow = db.select().from(albums).where(eq(albums.id, album.id)).get();
    expect(albumRow?.cover_photo_id).toBe(photo.id);
  });

  it('throws ValidationError for invalid file type', async () => {
    const { ValidationError } = await import('@/lib/validation/file-validation');
    const album = await createAlbum(db, { name: 'Invalid Test', date: '2026-06-03' });
    const pdfBuffer = Buffer.from('%PDF-1.4 fake content');
    await expect(addPhoto(db, album.id, pdfBuffer, 'fake.pdf', TEST_DATA)).rejects.toThrow(ValidationError);
  });
});

describe('removePhoto', () => {
  it('deletes photo row and files from disk', async () => {
    const album = await createAlbum(db, { name: 'Remove Test', date: '2026-06-04' });
    const photo = await addPhoto(db, album.id, sampleJpgBuffer, 'remove.jpg', TEST_DATA);

    const imagePath = getImagePath(db, photo.id, TEST_DATA)!;
    const thumbPath = getThumbnailPath(db, photo.id, TEST_DATA)!;

    const result = removePhoto(db, photo.id, TEST_DATA);
    expect(result).toBe(true);
    expect(fs.existsSync(imagePath)).toBe(false);
    expect(fs.existsSync(thumbPath)).toBe(false);
  });

  it('returns false for non-existent photo', () => {
    const result = removePhoto(db, 99999, TEST_DATA);
    expect(result).toBe(false);
  });

  it('updates album cover after cover photo is removed', async () => {
    const { albums } = await import('@/lib/db/schema');
    const { eq } = await import('drizzle-orm');
    const album = await createAlbum(db, { name: 'Cover Update', date: '2026-06-05' });
    const p1 = await addPhoto(db, album.id, sampleJpgBuffer, 'p1.jpg', TEST_DATA);
    const p2 = await addPhoto(db, album.id, sampleJpgBuffer, 'p2.jpg', TEST_DATA);

    removePhoto(db, p1.id, TEST_DATA);

    const albumRow = db.select().from(albums).where(eq(albums.id, album.id)).get();
    expect(albumRow?.cover_photo_id).toBe(p2.id);
  });
});

describe('getImagePath / getThumbnailPath', () => {
  it('returns null for non-existent photo', () => {
    expect(getImagePath(db, 99999, TEST_DATA)).toBeNull();
    expect(getThumbnailPath(db, 99999, TEST_DATA)).toBeNull();
  });
});
