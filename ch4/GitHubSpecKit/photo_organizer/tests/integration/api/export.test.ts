import path from 'path';
import fs from 'fs';
import sharp from 'sharp';
import { eq } from 'drizzle-orm';
import { createTestDb, closeDb } from '@/lib/db/client';
import { createAlbum } from '@/lib/services/album-service';
import { addPhoto, getPhotoById } from '@/lib/services/photo-service';
import { photos as photosTable } from '@/lib/db/schema';
import type { EffectChain } from '@/types';

const TEST_DB = path.join(__dirname, '../../../data/test-export-integration.db');
const TEST_DATA = path.join(__dirname, '../../../data/test-export-data');

let db: ReturnType<typeof createTestDb>;
let jpgBuffer: Buffer;
let albumId: number;
let photoIds: number[];

beforeAll(async () => {
  fs.mkdirSync(path.dirname(TEST_DB), { recursive: true });
  fs.mkdirSync(TEST_DATA, { recursive: true });
  if (fs.existsSync(TEST_DB)) fs.unlinkSync(TEST_DB);
  db = createTestDb(TEST_DB);

  jpgBuffer = await sharp({
    create: { width: 100, height: 100, channels: 3, background: { r: 100, g: 150, b: 200 } },
  }).jpeg({ quality: 80 }).toBuffer();

  const album = await createAlbum(db, { name: 'Export Test', date: '2026-06-17' });
  albumId = album.id;
  photoIds = [];
  for (let i = 0; i < 3; i++) {
    const p = await addPhoto(db, albumId, jpgBuffer, `test-${i}.jpg`, TEST_DATA);
    photoIds.push(p.id);
  }
});

afterAll(() => {
  closeDb(db);
  if (fs.existsSync(TEST_DB)) fs.unlinkSync(TEST_DB);
  fs.rmSync(TEST_DATA, { recursive: true, force: true });
});

describe('buildZipStream', () => {
  async function getPhotoRows(ids: number[]) {
    return ids.map((id) => {
      const row = db.select().from(photosTable).where(eq(photosTable.id, id)).get()!;
      return { id: row.id, filepath: row.filepath, filename: row.filename };
    });
  }

  it('returns a readable stream with ZIP magic bytes for a non-empty photo list', async () => {
    const { buildZipStream } = await import('@/lib/services/export-service');
    const rows = await getPhotoRows(photoIds);
    const chain: EffectChain = [{ type: 'grayscale', intensity: 100 }];

    const stream = buildZipStream(rows, chain, 'jpeg', TEST_DATA);
    const chunks: Buffer[] = [];
    await new Promise<void>((resolve, reject) => {
      stream.on('data', (c: Buffer) => chunks.push(c));
      stream.on('end', resolve);
      stream.on('error', reject);
    });

    const zip = Buffer.concat(chunks);
    expect(zip[0]).toBe(0x50); // PK magic
    expect(zip[1]).toBe(0x4b);
    expect(zip.length).toBeGreaterThan(100);
  });

  it('applies no effects when chain is empty', async () => {
    const { buildZipStream } = await import('@/lib/services/export-service');
    const rows = await getPhotoRows([photoIds[0]]);
    const stream = buildZipStream(rows, [], 'jpeg', TEST_DATA);
    const chunks: Buffer[] = [];
    await new Promise<void>((resolve, reject) => {
      stream.on('data', (c: Buffer) => chunks.push(c));
      stream.on('end', resolve);
      stream.on('error', reject);
    });
    const zip = Buffer.concat(chunks);
    expect(zip[0]).toBe(0x50);
  });

  it('throws when the photo list is empty', async () => {
    const { buildZipStream } = await import('@/lib/services/export-service');
    expect(() => buildZipStream([], [], 'jpeg', TEST_DATA)).toThrow('No photos to export');
  });
});

describe('photo DB lookups for export', () => {
  it('finds all seeded photos by id', () => {
    for (const id of photoIds) {
      expect(getPhotoById(db, id)).not.toBeNull();
    }
  });

  it('returns null for a missing photo', () => {
    expect(getPhotoById(db, 99999)).toBeNull();
  });
});
