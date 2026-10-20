import type { Metadata } from 'next'
import Link from 'next/link'
import { createNoteAction } from '@/app/actions'
import { SubmitButton } from './submit-button'

export const metadata: Metadata = { title: 'New Note' }

export default function NewNotePage() {
  return (
    <div>
      <div className="page-header">
        <h1>New Note</h1>
        <Link href="/" className="btn btn-secondary">Cancel</Link>
      </div>

      <div className="card">
        <form action={createNoteAction} className="form">
          <div className="field">
            <label htmlFor="title">Title</label>
            <input
              id="title"
              name="title"
              type="text"
              placeholder="Note title..."
              required
              autoFocus
            />
          </div>

          <div className="field">
            <label htmlFor="content">Content</label>
            <textarea
              id="content"
              name="content"
              placeholder="Write your note here..."
              required
            />
          </div>

          <div className="actions">
            <SubmitButton />
            <Link href="/" className="btn btn-secondary">Cancel</Link>
          </div>
        </form>
      </div>
    </div>
  )
}
