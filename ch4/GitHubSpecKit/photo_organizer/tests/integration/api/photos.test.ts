import path from 'path';
import fs from 'fs';
import sharp from 'sharp';
import { createTestDb, closeDb } from '@/lib/db/client';
import { createAlbum } from '@/lib/services/album-service';
import { addPhoto, getImagePath, getThumbnailPath, getPhotoById, removePhoto } from '@/lib/services/photo-service';

const TEST_DB = path.join(__dirname, '../../../data/test-photos-integration.db');
const TEST_DATA = path.join(__dirname, '../../../data/test-photos-data');

let db: ReturnType<typeof createTestDb>;
let jpgBuffer: Buffer;

beforeAll(async () => {
  fs.mkdirSync(path.dirname(TEST_DB), { recursive: true });
  fs.mkdirSync(TEST_DATA, { recursive: true });

  if (fs.existsSync(TEST_DB)) fs.unlinkSync(TEST_DB);
  db = createTestDb(TEST_DB);

  jpgBuffer = await sharp({
    create: { width: 100, height: 100, channels: 3, background: { r: 128, g: 64, b: 32 } },
  }).jpeg({ quality: 80 }).toBuffer();
});

afterAll(() => {
  closeDb(db);
  if (fs.existsSync(TEST_DB)) fs.unlinkSync(TEST_DB);
  fs.rmSync(TEST_DATA, { recursive: true, force: true });
});

describe('Photo service — integration', () => {
  it('adds a photo and serves it from correct paths', async () => {
    const album = await createAlbum(db, { name: 'Integration Album', date: '2026-06-01' });
    const photo = await addPhoto(db, album.id, jpgBuffer, 'test.jpg', TEST_DATA);

    expect(photo.id).toBeGreaterThan(0);
    expect(photo.mimeType).toBe('image/jpeg');

    const imagePath = getImagePath(db, photo.id, TEST_DATA);
    const thumbPath = getThumbnailPath(db, photo.id, TEST_DATA);

    expect(imagePath).toBeTruthy();
    expect(thumbPath).toBeTruthy();
    expect(fs.existsSync(imagePath!)).toBe(true);
    expect(fs.existsSync(thumbPath!)).toBe(true);

    // Thumbnail should be ≤ 400×400
    const thumbMeta = await sharp(thumbPath!).metadata();
    expect(thumbMeta.width).toBeLessThanOrEqual(400);
    expect(thumbMeta.height).toBeLessThanOrEqual(400);
  });

  it('getPhotoById returns null for missing photo', () => {
    expect(getPhotoById(db, 99999)).toBeNull();
  });

  it('removes photo and cleans up files', async () => {
    const album = await createAlbum(db, { name: 'Remove Album', date: '2026-06-02' });
    const photo = await addPhoto(db, album.id, jpgBuffer, 'remove.jpg', TEST_DATA);

    const img = getImagePath(db, photo.id, TEST_DATA)!;
    removePhoto(db, photo.id, TEST_DATA);
    expect(fs.existsSync(img)).toBe(false);
    expect(getPhotoById(db, photo.id)).toBeNull();
  });

  it('rejects non-image files', async () => {
    const { ValidationError } = await import('@/lib/validation/file-validation');
    const album = await createAlbum(db, { name: 'Reject Album', date: '2026-06-03' });
    const pdfBuf = Buffer.from('%PDF-1.4 fake content');
    await expect(addPhoto(db, album.id, pdfBuf, 'bad.pdf', TEST_DATA)).rejects.toThrow(ValidationError);
  });
});
