import path from 'path';
import fs from 'fs';
import { createTestDb, closeDb } from '@/lib/db/client';
import {
  getAllAlbums,
  getAlbumById,
  reorderAlbum,
  createAlbum,
  updateAlbum,
  deleteAlbum,
} from '@/lib/services/album-service';

const TEST_DB = path.join(__dirname, '../../../data/test-album-service.db');

let db: ReturnType<typeof createTestDb>;

beforeAll(() => {
  fs.mkdirSync(path.dirname(TEST_DB), { recursive: true });
  if (fs.existsSync(TEST_DB)) fs.unlinkSync(TEST_DB);
  db = createTestDb(TEST_DB);
});

afterAll(() => {
  closeDb(db);
  if (fs.existsSync(TEST_DB)) fs.unlinkSync(TEST_DB);
});

// ── getAll / getById ──────────────────────────────────────────────────────────

describe('getAllAlbums', () => {
  it('returns empty array when no albums exist', async () => {
    const result = await getAllAlbums(db);
    expect(result).toEqual([]);
  });

  it('returns albums ordered by display_order', async () => {
    await createAlbum(db, { name: 'B Album', date: '2026-06-01' });
    await createAlbum(db, { name: 'A Album', date: '2026-05-01' });
    const result = await getAllAlbums(db);
    expect(result.length).toBe(2);
    expect(result[0].displayOrder).toBeLessThan(result[1].displayOrder);
  });
});

describe('getAlbumById', () => {
  it('returns null for non-existent album', async () => {
    const result = await getAlbumById(db, 999);
    expect(result).toBeNull();
  });

  it('returns album with photo list', async () => {
    const album = await createAlbum(db, { name: 'Test', date: '2026-06-15' });
    const result = await getAlbumById(db, album.id);
    expect(result).not.toBeNull();
    expect(result!.photos).toEqual([]);
  });
});

// ── reorder ───────────────────────────────────────────────────────────────────

describe('reorderAlbum', () => {
  let albumId: number;

  beforeEach(async () => {
    const a = await createAlbum(db, { name: 'Reorder Test', date: '2026-01-01' });
    albumId = a.id;
  });

  it('places album between two others using mid-point', async () => {
    const updated = await reorderAlbum(db, albumId, { predecessorOrder: 1000, successorOrder: 3000 });
    expect(updated.displayOrder).toBe(2000);
  });

  it('places album at start when no predecessor given', async () => {
    const updated = await reorderAlbum(db, albumId, { successorOrder: 1000 });
    expect(updated.displayOrder).toBe(500);
  });

  it('places album at end when no successor given', async () => {
    const updated = await reorderAlbum(db, albumId, { predecessorOrder: 5000 });
    expect(updated.displayOrder).toBe(6000);
  });

  it('triggers renormalization when gap shrinks below 0.001', async () => {
    // Force a tiny gap
    const updated = await reorderAlbum(db, albumId, {
      predecessorOrder: 1000,
      successorOrder: 1000.0009,
    });
    // After renormalization all orders are multiples of 1000 — updated value is ≥ 1000
    expect(updated.displayOrder % 1000).toBe(0);
  });
});

// ── createAlbum ───────────────────────────────────────────────────────────────

describe('createAlbum', () => {
  it('creates album with correct fields', async () => {
    const album = await createAlbum(db, { name: 'New Album', date: '2026-07-04' });
    expect(album.name).toBe('New Album');
    expect(album.date).toBe('2026-07-04');
    expect(album.coverPhotoId).toBeNull();
    expect(album.photoCount).toBe(0);
  });

  it('assigns display_order as max + 1000', async () => {
    const a1 = await createAlbum(db, { name: 'First', date: '2026-01-01' });
    const a2 = await createAlbum(db, { name: 'Second', date: '2026-02-01' });
    expect(a2.displayOrder).toBe(a1.displayOrder + 1000);
  });
});

// ── updateAlbum ───────────────────────────────────────────────────────────────

describe('updateAlbum', () => {
  it('updates name and date', async () => {
    const album = await createAlbum(db, { name: 'Old Name', date: '2026-01-01' });
    const updated = await updateAlbum(db, album.id, { name: 'New Name', date: '2026-12-31' });
    expect(updated!.name).toBe('New Name');
    expect(updated!.date).toBe('2026-12-31');
  });

  it('returns null for non-existent album', async () => {
    const result = await updateAlbum(db, 99999, { name: 'X' });
    expect(result).toBeNull();
  });
});

// ── deleteAlbum ───────────────────────────────────────────────────────────────

describe('deleteAlbum', () => {
  it('returns true when album existed and is deleted', async () => {
    const album = await createAlbum(db, { name: 'Delete Me', date: '2026-01-01' });
    const result = await deleteAlbum(db, album.id, path.join(__dirname, '../../../data'));
    expect(result).toBe(true);
    expect(await getAlbumById(db, album.id)).toBeNull();
  });

  it('returns false for non-existent album', async () => {
    const result = await deleteAlbum(db, 99999, path.join(__dirname, '../../../data'));
    expect(result).toBe(false);
  });
});
