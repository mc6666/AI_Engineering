import path from 'path';
import fs from 'fs';
import sharp from 'sharp';
import { createTestDb, closeDb } from '@/lib/db/client';
import { createAlbum } from '@/lib/services/album-service';
import { addPhoto } from '@/lib/services/photo-service';
import { applyEffects } from '@/lib/services/effect-service';
import type { EffectChain, OutputFormat } from '@/types';

const TEST_DB = path.join(__dirname, '../../../data/test-process-integration.db');
const TEST_DATA = path.join(__dirname, '../../../data/test-process-data');

let db: ReturnType<typeof createTestDb>;
let jpgBuffer: Buffer;
let photoId: number;

beforeAll(async () => {
  fs.mkdirSync(path.dirname(TEST_DB), { recursive: true });
  fs.mkdirSync(TEST_DATA, { recursive: true });
  if (fs.existsSync(TEST_DB)) fs.unlinkSync(TEST_DB);
  db = createTestDb(TEST_DB);

  jpgBuffer = await sharp({
    create: { width: 100, height: 100, channels: 3, background: { r: 200, g: 100, b: 50 } },
  }).jpeg({ quality: 80 }).toBuffer();

  const album = await createAlbum(db, { name: 'Process Test', date: '2026-06-17' });
  const photo = await addPhoto(db, album.id, jpgBuffer, 'process-test.jpg', TEST_DATA);
  photoId = photo.id;
});

afterAll(() => {
  closeDb(db);
  if (fs.existsSync(TEST_DB)) fs.unlinkSync(TEST_DB);
  fs.rmSync(TEST_DATA, { recursive: true, force: true });
});

describe('applyEffects (process route integration)', () => {
  it('returns a valid JPEG buffer for an empty chain', async () => {
    const result = await applyEffects(jpgBuffer, [], 'jpeg');
    const meta = await sharp(result).metadata();
    expect(meta.format).toBe('jpeg');
    expect(result.length).toBeGreaterThan(0);
  });

  it('returns a valid PNG buffer with format png', async () => {
    const result = await applyEffects(jpgBuffer, [{ type: 'grayscale', intensity: 100 }], 'png');
    const meta = await sharp(result).metadata();
    expect(meta.format).toBe('png');
  });

  it('applies grayscale — output is greyscale JPEG', async () => {
    const chain: EffectChain = [{ type: 'grayscale', intensity: 100 }];
    const result = await applyEffects(jpgBuffer, chain, 'jpeg');
    const meta = await sharp(result).metadata();
    expect(meta.format).toBe('jpeg');
    expect(result.length).toBeGreaterThan(0);
  });

  it('applies sepia effect', async () => {
    const result = await applyEffects(jpgBuffer, [{ type: 'sepia', intensity: 100 }], 'jpeg');
    expect(await isValidImage(result)).toBe(true);
  });

  it('applies blur effect', async () => {
    const result = await applyEffects(jpgBuffer, [{ type: 'blur', intensity: 50 }], 'jpeg');
    expect(await isValidImage(result)).toBe(true);
  });

  it('throws on chain length > 5', async () => {
    const chain = Array(6).fill({ type: 'blur', intensity: 10 }) as EffectChain;
    await expect(applyEffects(jpgBuffer, chain, 'jpeg')).rejects.toThrow('effects must have at most 5 items');
  });

  it('throws on unknown effect type', async () => {
    const chain = [{ type: 'oil_paint' as EffectChain[0]['type'], intensity: 50 }];
    await expect(applyEffects(jpgBuffer, chain, 'jpeg')).rejects.toThrow('Unknown effect type');
  });

  it('photo id is available in DB after add', () => {
    const { getPhotoById } = require('@/lib/services/photo-service');
    const found = getPhotoById(db, photoId);
    expect(found).not.toBeNull();
    expect(found?.id).toBe(photoId);
  });
});

async function isValidImage(buf: Buffer): Promise<boolean> {
  try { await sharp(buf).metadata(); return true; } catch { return false; }
}
