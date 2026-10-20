import type { Metadata } from 'next'
import Link from 'next/link'
import { getAllNotes } from '@/lib/notes'

export const metadata: Metadata = { title: 'All Notes' }

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

export default function HomePage() {
  const notes = getAllNotes()

  return (
    <div>
      <div className="page-header">
        <h1>My Notes</h1>
        <span style={{ color: 'var(--text-muted)', fontSize: '.9rem' }}>
          {notes.length} {notes.length === 1 ? 'note' : 'notes'}
        </span>
      </div>

      {notes.length === 0 ? (
        <div className="empty">
          <h2>No notes yet</h2>
          <p>Create your first note to get started.</p>
          <br />
          <Link href="/notes/new" className="btn btn-primary">+ New Note</Link>
        </div>
      ) : (
        <div className="notes-grid">
          {notes.map((note) => (
            <Link key={note.id} href={`/notes/${note.id}`} className="note-card">
              <h2>{note.title}</h2>
              <p className="preview">{note.content}</p>
              <p className="meta">Updated {formatDate(note.updatedAt)}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
