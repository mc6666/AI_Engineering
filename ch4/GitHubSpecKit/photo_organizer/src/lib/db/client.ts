import Database from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';
import path from 'path';
import fs from 'fs';
import * as schema from './schema';

const DB_URL = process.env.DATABASE_URL ?? './data/photo-organizer.db';

function applyMigrations(sqlite: Database.Database): void {
  const migrationsDir = path.join(__dirname, 'migrations');
  if (!fs.existsSync(migrationsDir)) return;

  sqlite.exec(`
    CREATE TABLE IF NOT EXISTS __migrations (
      filename TEXT PRIMARY KEY,
      applied_at TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP)
    )
  `);

  const applied = new Set(
    (sqlite.prepare('SELECT filename FROM __migrations').all() as { filename: string }[])
      .map((r) => r.filename)
  );

  const files = fs.readdirSync(migrationsDir)
    .filter((f) => f.endsWith('.sql'))
    .sort();

  for (const file of files) {
    if (applied.has(file)) continue;
    const sql = fs.readFileSync(path.join(migrationsDir, file), 'utf8');
    sqlite.exec(sql);
    sqlite.prepare('INSERT INTO __migrations (filename) VALUES (?)').run(file);
  }
}

function createConnection(dbUrl: string): ReturnType<typeof drizzle> {
  const dbPath = path.resolve(dbUrl);
  fs.mkdirSync(path.dirname(dbPath), { recursive: true });

  const sqlite = new Database(dbPath);
  sqlite.pragma('journal_mode = WAL');
  sqlite.pragma('foreign_keys = ON');

  applyMigrations(sqlite);

  return drizzle(sqlite, { schema });
}

// Singleton: reuse connection across hot-reloads in Next.js dev
const g = globalThis as typeof globalThis & { _db?: ReturnType<typeof drizzle> };
export const db = g._db ?? (g._db = createConnection(DB_URL));

export function createTestDb(dbPath: string): ReturnType<typeof drizzle> {
  return createConnection(dbPath);
}

export function closeDb(drizzleDb: ReturnType<typeof drizzle>): void {
  // Access the underlying better-sqlite3 Database instance to close it.
  // Needed on Windows where open SQLite files cannot be deleted.
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (drizzleDb as any).session?.client?.close?.();
}
