import "server-only";

import Database from "better-sqlite3";
import fs from "node:fs";
import path from "node:path";
import type { NoteInput, NoteRecord, NoteSummary } from "@/lib/types";

const dataDir = path.join(process.cwd(), "data");
const dbPath = path.join(dataDir, "notes.sqlite");

let db: Database.Database | null = null;

function ensureDatabase() {
  if (db) return db;

  fs.mkdirSync(dataDir, { recursive: true });
  db = new Database(dbPath);
  db.pragma("journal_mode = WAL");
  db.pragma("foreign_keys = ON");
  db.exec(`
    CREATE TABLE IF NOT EXISTS notes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      note_title TEXT NOT NULL,
      article_title TEXT NOT NULL DEFAULT '',
      article_link TEXT NOT NULL DEFAULT '',
      tags TEXT NOT NULL DEFAULT '',
      content TEXT NOT NULL DEFAULT '',
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_notes_updated_at ON notes(updated_at DESC);
    CREATE INDEX IF NOT EXISTS idx_notes_note_title ON notes(note_title);
    CREATE INDEX IF NOT EXISTS idx_notes_tags ON notes(tags);
  `);

  const count = db.prepare("SELECT COUNT(*) AS count FROM notes").get() as { count: number };
  if (count.count === 0) {
    const seed = db.prepare(`
      INSERT INTO notes (note_title, article_title, article_link, tags, content, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `);
    seed.run(
      "First note",
      "Demo article title",
      "https://example.com/article",
      "demo, markdown",
      "# Welcome\n\nThis notebook supports Markdown editing with a live preview.\n\n- Headings\n- Lists\n- Links\n",
      new Date().toISOString(),
      new Date().toISOString()
    );
    seed.run(
      "Work ideas",
      "Product design notes",
      "https://example.com/design",
      "work, idea, design",
      "## Direction\n\n1. Collect requirements\n2. Shape the data model\n3. Wire search and tags\n",
      new Date().toISOString(),
      new Date().toISOString()
    );
  }

  return db;
}

function parseTags(tags: string) {
  return tags
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);
}

function serializeTags(tags: string[]) {
  return tags
    .map((tag) => tag.trim())
    .filter(Boolean)
    .join(", ");
}

function toSummary(row: any): NoteSummary {
  return {
    id: row.id,
    noteTitle: row.note_title,
    articleTitle: row.article_title,
    articleLink: row.article_link,
    tags: parseTags(row.tags),
    contentExcerpt: String(row.content || "")
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, 160),
    updatedAt: row.updated_at
  };
}

function toRecord(row: any): NoteRecord {
  const summary = toSummary(row);
  return {
    ...summary,
    content: row.content,
    createdAt: row.created_at
  };
}

export function listNotes(query = ""): NoteSummary[] {
  const database = ensureDatabase();
  const search = `%${query.trim().toLowerCase()}%`;
  const rows = query.trim()
    ? database.prepare(
        `
        SELECT *
        FROM notes
        WHERE lower(note_title) LIKE ?
           OR lower(article_title) LIKE ?
           OR lower(tags) LIKE ?
           OR lower(content) LIKE ?
        ORDER BY updated_at DESC, id DESC
      `
      ).all(search, search, search, search)
    : database.prepare(
        `
        SELECT *
        FROM notes
        ORDER BY updated_at DESC, id DESC
      `
      ).all();

  return rows.map(toSummary);
}

export function getNote(id: number): NoteRecord | null {
  const database = ensureDatabase();
  const row = database.prepare("SELECT * FROM notes WHERE id = ?").get(id);
  return row ? toRecord(row) : null;
}

export function createNote(input?: Partial<NoteInput>): NoteRecord {
  const database = ensureDatabase();
  const payload = normalizeInput({
    noteTitle: input?.noteTitle,
    articleTitle: input?.articleTitle,
    articleLink: input?.articleLink,
    tags: input?.tags,
    content: input?.content
  });

  const statement = database.prepare(`
    INSERT INTO notes (note_title, article_title, article_link, tags, content, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `);
  const result = statement.run(
    payload.noteTitle,
    payload.articleTitle,
    payload.articleLink,
    serializeTags(payload.tags),
    payload.content,
    new Date().toISOString(),
    new Date().toISOString()
  );

  const note = getNote(Number(result.lastInsertRowid));
  if (!note) {
    throw new Error("Failed to load newly created note.");
  }
  return note;
}

export function updateNote(id: number, input: NoteInput): NoteRecord | null {
  const database = ensureDatabase();
  const payload = normalizeInput(input);
  const statement = database.prepare(`
    UPDATE notes
    SET note_title = ?, article_title = ?, article_link = ?, tags = ?, content = ?, updated_at = ?
    WHERE id = ?
  `);
  const result = statement.run(
    payload.noteTitle,
    payload.articleTitle,
    payload.articleLink,
    serializeTags(payload.tags),
    payload.content,
    new Date().toISOString(),
    id
  );
  if (result.changes === 0) return null;
  return getNote(id);
}

export function deleteNote(id: number) {
  const database = ensureDatabase();
  const result = database.prepare("DELETE FROM notes WHERE id = ?").run(id);
  return result.changes > 0;
}

function normalizeInput(
  input: Partial<Omit<NoteInput, "tags">> & { tags?: string[] | string }
): NoteInput {
  const tags = Array.isArray(input.tags)
    ? input.tags
    : typeof input.tags === "string"
      ? input.tags.split(",")
      : [];

  return {
    noteTitle: (input.noteTitle ?? "Untitled note").trim() || "Untitled note",
    articleTitle: (input.articleTitle ?? "").trim(),
    articleLink: (input.articleLink ?? "").trim(),
    tags: tags.map((tag) => tag.trim()).filter(Boolean),
    content: input.content ?? ""
  };
}
