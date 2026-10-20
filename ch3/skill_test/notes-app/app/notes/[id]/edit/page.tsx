import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getNoteById } from '@/lib/notes'
import { updateNoteAction } from '@/app/actions'
import { SubmitButton } from './submit-button'

type Props = { params: Promise<{ id: string }> }

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params
  const note = getNoteById(id)
  return { title: note ? `Edit: ${note.title}` : 'Not found' }
}

export default async function EditNotePage({ params }: Props) {
  const { id } = await params
  const note = getNoteById(id)

  if (!note) notFound()

  const action = updateNoteAction.bind(null, note.id)

  return (
    <div>
      <div className="page-header">
        <h1>Edit Note</h1>
        <Link href={`/notes/${note.id}`} className="btn btn-secondary">Cancel</Link>
      </div>

      <div className="card">
        <form action={action} className="form">
          <div className="field">
            <label htmlFor="title">Title</label>
            <input
              id="title"
              name="title"
              type="text"
              defaultValue={note.title}
              required
              autoFocus
            />
          </div>

          <div className="field">
            <label htmlFor="content">Content</label>
            <textarea
              id="content"
              name="content"
              defaultValue={note.content}
              required
            />
          </div>

          <div className="actions">
            <SubmitButton />
            <Link href={`/notes/${note.id}`} className="btn btn-secondary">Cancel</Link>
          </div>
        </form>
      </div>
    </div>
  )
}
