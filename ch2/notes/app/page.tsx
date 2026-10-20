import NotesApp from "@/components/notes-app";
import { listNotes, getNote } from "@/lib/db";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export default function Page() {
  const notes = listNotes();
  const selectedNote = notes.length > 0 ? getNote(notes[0].id) : null;

  return <NotesApp initialNotes={notes} initialSelectedNote={selectedNote} />;
}
