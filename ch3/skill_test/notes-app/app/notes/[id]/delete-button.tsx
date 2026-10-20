'use client'

import { useTransition } from 'react'
import { deleteNoteAction } from '@/app/actions'

export function DeleteButton({ id }: { id: string }) {
  const [pending, startTransition] = useTransition()

  function handleDelete() {
    if (!confirm('Delete this note? This cannot be undone.')) return
    startTransition(() => deleteNoteAction(id))
  }

  return (
    <button className="btn btn-danger" onClick={handleDelete} disabled={pending}>
      {pending ? 'Deleting...' : 'Delete'}
    </button>
  )
}
