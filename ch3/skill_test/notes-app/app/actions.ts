'use server'

import { redirect } from 'next/navigation'
import { createNote, updateNote, deleteNote } from '@/lib/notes'

export async function createNoteAction(formData: FormData) {
  const title = (formData.get('title') as string).trim()
  const content = (formData.get('content') as string).trim()

  if (!title || !content) return

  const note = createNote(title, content)
  redirect(`/notes/${note.id}`)
}

export async function updateNoteAction(id: string, formData: FormData) {
  const title = (formData.get('title') as string).trim()
  const content = (formData.get('content') as string).trim()

  if (!title || !content) return

  updateNote(id, title, content)
  redirect(`/notes/${id}`)
}

export async function deleteNoteAction(id: string) {
  deleteNote(id)
  redirect('/')
}
