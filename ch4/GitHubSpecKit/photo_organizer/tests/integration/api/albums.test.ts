/**
 * Integration tests for /api/albums and /api/albums/[id]/reorder.
 * Uses a real SQLite test DB — no mocking per constitution Principle II.
 */
import path from 'path';
import fs from 'fs';
import { createTestDb, closeDb } from '@/lib/db/client';
import { createAlbum, getAllAlbums } from '@/lib/services/album-service';
import { albums, photos } from '@/lib/db/schema';

const TEST_DB = path.join(__dirname, '../../../data/test-albums-integration.db');
const DATA_DIR = path.join(__dirname, '../../../data');

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

beforeEach(() => {
  db.delete(photos).run();
  db.delete(albums).run();
});

describe('GET /api/albums — album list', () => {
  it('returns empty list when no albums exist', async () => {
    const albums = await getAllAlbums(db);
    expect(albums).toEqual([]);
  });

  it('returns albums sorted by display_order', async () => {
    await createAlbum(db, { name: 'Alpha', date: '2026-01-01' });
    await createAlbum(db, { name: 'Beta', date: '2026-02-01' });
    const result = await getAllAlbums(db);
    expect(result.length).toBe(2);
    expect(result[0].displayOrder).toBeLessThan(result[1].displayOrder);
  });

  it('includes correct photo count and coverThumbnailUrl', async () => {
    const album = await createAlbum(db, { name: 'Test', date: '2026-03-01' });
    const result = await getAllAlbums(db);
    expect(result[0].photoCount).toBe(0);
    expect(result[0].coverThumbnailUrl).toBeNull();
    expect(result[0].id).toBe(album.id);
  });
});

describe('POST /api/albums/[id]/reorder', () => {
  it('updates display_order for moved album', async () => {
    const { reorderAlbum } = await import('@/lib/services/album-service');
    const a1 = await createAlbum(db, { name: 'A1', date: '2026-01-01' });
    const a2 = await createAlbum(db, { name: 'A2', date: '2026-02-01' });
    const a3 = await createAlbum(db, { name: 'A3', date: '2026-03-01' });

    // Move A3 between A1 and A2
    const updated = await reorderAlbum(db, a3.id, {
      predecessorOrder: a1.displayOrder,
      successorOrder: a2.displayOrder,
    });

    expect(updated.displayOrder).toBeGreaterThan(a1.displayOrder);
    expect(updated.displayOrder).toBeLessThan(a2.displayOrder);
  });

  it('persists reorder across subsequent reads', async () => {
    const { reorderAlbum } = await import('@/lib/services/album-service');
    const a1 = await createAlbum(db, { name: 'First', date: '2026-01-01' });
    const a2 = await createAlbum(db, { name: 'Second', date: '2026-02-01' });

    // Move a2 before a1
    await reorderAlbum(db, a2.id, { successorOrder: a1.displayOrder });

    const list = await getAllAlbums(db);
    expect(list[0].id).toBe(a2.id);
    expect(list[1].id).toBe(a1.id);
  });
});

describe('POST /api/albums — create', () => {
  it('creates album with provided name and date', async () => {
    const album = await createAlbum(db, { name: 'Birthday', date: '2026-06-10' });
    expect(album.name).toBe('Birthday');
    expect(album.date).toBe('2026-06-10');
    expect(typeof album.id).toBe('number');
  });
});

describe('DELETE /api/albums/[id]', () => {
  it('deletes album from db', async () => {
    const { deleteAlbum, getAlbumById } = await import('@/lib/services/album-service');
    const album = await createAlbum(db, { name: 'Remove Me', date: '2026-01-01' });
    await deleteAlbum(db, album.id, DATA_DIR);
    expect(await getAlbumById(db, album.id)).toBeNull();
  });
});
