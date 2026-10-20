import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getNoteById } from '@/lib/notes'
import { DeleteButton } from './delete-button'

type Props = { params: Promise<{ id: string }> }

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params
  const note = getNoteById(id)
  return { title: note?.title ?? 'Note not found' }
}

function formatDateTime(iso: string) {
  return new Date(iso).toLocaleString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

export default async function NoteDetailPage({ params }: Props) {
  const { id } = await params
  const note = getNoteById(id)

  if (!note) notFound()

  return (
    <div>
      <div className="page-header">
        <Link href="/" className="btn btn-secondary">← Back</Link>
        <div className="actions">
          <Link href={`/notes/${note.id}/edit`} className="btn btn-secondary">Edit</Link>
          <DeleteButton id={note.id} />
        </div>
      </div>

      <div className="card">
        <h1 className="note-title">{note.title}</h1>
        <p className="note-meta">
          Created {formatDateTime(note.createdAt)}
          {note.updatedAt !== note.createdAt && (
            <> &middot; Updated {formatDateTime(note.updatedAt)}</>
          )}
        </p>
        <hr className="divider" />
        <p className="note-content">{note.content}</p>
      </div>
    </div>
  )
}
