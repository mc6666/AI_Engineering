import fs from 'fs'
import path from 'path'
import { v4 as uuidv4 } from 'uuid'

export type Note = {
  id: string
  title: string
  content: string
  createdAt: string
  updatedAt: string
}

const DB_PATH = path.join(process.cwd(), 'data', 'notes.json')

function readDb(): Note[] {
  if (!fs.existsSync(DB_PATH)) {
    fs.mkdirSync(path.dirname(DB_PATH), { recursive: true })
    fs.writeFileSync(DB_PATH, '[]', 'utf-8')
    return []
  }
  return JSON.parse(fs.readFileSync(DB_PATH, 'utf-8')) as Note[]
}

function writeDb(notes: Note[]): void {
  fs.writeFileSync(DB_PATH, JSON.stringify(notes, null, 2), 'utf-8')
}

export function getAllNotes(): Note[] {
  return readDb().sort(
    (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
  )
}

export function getNoteById(id: string): Note | null {
  return readDb().find((n) => n.id === id) ?? null
}

export function createNote(title: string, content: string): Note {
  const notes = readDb()
  const now = new Date().toISOString()
  const note: Note = { id: uuidv4(), title, content, createdAt: now, updatedAt: now }
  writeDb([...notes, note])
  return note
}

export function updateNote(id: string, title: string, content: string): Note | null {
  const notes = readDb()
  const idx = notes.findIndex((n) => n.id === id)
  if (idx === -1) return null
  notes[idx] = { ...notes[idx], title, content, updatedAt: new Date().toISOString() }
  writeDb(notes)
  return notes[idx]
}

export function deleteNote(id: string): boolean {
  const notes = readDb()
  const filtered = notes.filter((n) => n.id !== id)
  if (filtered.length === notes.length) return false
  writeDb(filtered)
  return true
}
