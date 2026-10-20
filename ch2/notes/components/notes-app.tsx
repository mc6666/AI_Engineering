"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useRef, useState } from "react";
import type { Options as EasyMDEOptions } from "easymde";
import type { NoteInput, NoteRecord, NoteSummary } from "@/lib/types";

const SimpleMDE = dynamic(() => import("react-simplemde-editor").then((mod) => mod.default), {
  ssr: false
});

type Props = {
  initialNotes: NoteSummary[];
  initialSelectedNote: NoteRecord | null;
};

type Draft = {
  noteTitle: string;
  articleTitle: string;
  articleLink: string;
  tags: string;
  content: string;
};

const emptyDraft: Draft = {
  noteTitle: "Untitled note",
  articleTitle: "",
  articleLink: "",
  tags: "",
  content: ""
};

function toDraft(note: NoteRecord): Draft {
  return {
    noteTitle: note.noteTitle,
    articleTitle: note.articleTitle,
    articleLink: note.articleLink,
    tags: note.tags.join(", "),
    content: note.content
  };
}

function toPayload(draft: Draft): NoteInput {
  return {
    noteTitle: draft.noteTitle,
    articleTitle: draft.articleTitle,
    articleLink: draft.articleLink,
    tags: draft.tags
      .split(",")
      .map((tag) => tag.trim())
      .filter(Boolean),
    content: draft.content
  };
}

function toSummary(note: NoteRecord): NoteSummary {
  return {
    id: note.id,
    noteTitle: note.noteTitle,
    articleTitle: note.articleTitle,
    articleLink: note.articleLink,
    tags: note.tags,
    contentExcerpt: note.contentExcerpt,
    updatedAt: note.updatedAt
  };
}

export default function NotesApp({ initialNotes, initialSelectedNote }: Props) {
  const [notes, setNotes] = useState(initialNotes);
  const [selectedId, setSelectedId] = useState<number | null>(initialSelectedNote?.id ?? initialNotes[0]?.id ?? null);
  const [selectedNote, setSelectedNote] = useState<NoteRecord | null>(initialSelectedNote);
  const [draft, setDraft] = useState<Draft>(initialSelectedNote ? toDraft(initialSelectedNote) : emptyDraft);
  const [query, setQuery] = useState("");
  const selectedIdRef = useRef<number | null>(selectedId);

  useEffect(() => {
    selectedIdRef.current = selectedId;
  }, [selectedId]);

  const hasArticleLink = draft.articleLink.trim().length > 0;

  const editorOptions = useMemo<EasyMDEOptions>(
    () => ({
      autofocus: false,
      spellChecker: false,
      status: false,
      placeholder: "# Heading\n\nWrite your note here...",
      minHeight: "420px",
      toolbar: [
        "bold",
        "italic",
        "heading",
        "|",
        "quote",
        "unordered-list",
        "ordered-list",
        "|",
        "link",
        "image",
        "table",
        "code",
        "|",
        "preview",
        "fullscreen"
      ] as EasyMDEOptions["toolbar"]
    }),
    []
  );

  useEffect(() => {
    const controller = new AbortController();
    const timeout = setTimeout(async () => {
      try {
        const response = await fetch(`/api/notes?q=${encodeURIComponent(query)}`, {
          signal: controller.signal
        });
        if (!response.ok) return;

        const data = (await response.json()) as { notes: NoteSummary[] };
        setNotes(data.notes);

        if (data.notes.length === 0) {
          setSelectedId(null);
          setSelectedNote(null);
          setDraft(emptyDraft);
          return;
        }

        const activeId = selectedIdRef.current;
        if (!data.notes.some((note) => note.id === activeId)) {
          setSelectedId(data.notes[0].id);
        }
      } catch (error) {
        if ((error as Error).name !== "AbortError") return;
      }
    }, 180);

    return () => {
      controller.abort();
      clearTimeout(timeout);
    };
  }, [query]);

  useEffect(() => {
    if (selectedId == null) return;

    const controller = new AbortController();

    (async () => {
      try {
        const response = await fetch(`/api/notes/${selectedId}`, { signal: controller.signal });
        if (!response.ok) return;

        const data = (await response.json()) as { note: NoteRecord };
        setSelectedNote(data.note);
        setDraft(toDraft(data.note));
      } catch (error) {
        if ((error as Error).name !== "AbortError") return;
      }
    })();

    return () => controller.abort();
  }, [selectedId]);

  useEffect(() => {
    if (!selectedId || !selectedNote) return;

    const timer = setTimeout(async () => {
      const payload = toPayload(draft);
      const current = toDraft(selectedNote);
      const changed =
        payload.noteTitle !== current.noteTitle ||
        payload.articleTitle !== current.articleTitle ||
        payload.articleLink !== current.articleLink ||
        payload.tags.join(", ") !== current.tags ||
        payload.content !== current.content;

      if (!changed) return;

      try {
        const response = await fetch(`/api/notes/${selectedId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (!response.ok) return;

        const data = (await response.json()) as { note: NoteRecord };
        setSelectedNote(data.note);
        setDraft(toDraft(data.note));
        setNotes((previous) => [toSummary(data.note), ...previous.filter((note) => note.id !== data.note.id)]);
      } catch {
        return;
      }
    }, 700);

    return () => clearTimeout(timer);
  }, [draft, selectedId, selectedNote]);

  async function createNewNote() {
    try {
      const response = await fetch("/api/notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          noteTitle: "Untitled note",
          articleTitle: "",
          articleLink: "",
          tags: [],
          content: ""
        })
      });

      if (!response.ok) return;

      const data = (await response.json()) as { note: NoteRecord };
      const summary = toSummary(data.note);

      setNotes((previous) => [summary, ...previous.filter((note) => note.id !== summary.id)]);
      setSelectedId(summary.id);
      setSelectedNote(data.note);
      setDraft(toDraft(data.note));
    } catch {
      return;
    }
  }

  async function deleteCurrentNote() {
    if (!selectedId) return;
    if (!window.confirm("Delete this note?")) return;

    try {
      const response = await fetch(`/api/notes/${selectedId}`, { method: "DELETE" });
      if (!response.ok) return;

      const remaining = notes.filter((note) => note.id !== selectedId);
      setNotes(remaining);

      if (remaining.length > 0) {
        setSelectedId(remaining[0].id);
      } else {
        setSelectedId(null);
        setSelectedNote(null);
        setDraft(emptyDraft);
      }
    } catch {
      return;
    }
  }

  function openArticleLink() {
    if (!hasArticleLink) return;
    window.open(draft.articleLink, "_blank", "noopener,noreferrer");
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="toolbar toolbar-actions">
          <input
            className="search"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search title, tags, content"
          />
          <div className="sidebar-actions">
            <button className="primary icon-button" onClick={createNewNote} type="button" aria-label="New note" title="New note">
              +
            </button>
            <button
              className="ghost icon-button danger-icon"
              onClick={deleteCurrentNote}
              type="button"
              aria-label="Delete note"
              title="Delete note"
              disabled={!selectedId}
            >
              ×
            </button>
          </div>
        </div>

        <div className="note-list">
          {notes.map((note) => (
            <button
              key={note.id}
              className={`note-card ${note.id === selectedId ? "active" : ""}`}
              onClick={() => setSelectedId(note.id)}
              type="button"
            >
              <strong>{note.noteTitle}</strong>
              {note.tags.length > 0 && (
                <div className="note-tags">
                  {note.tags.slice(0, 3).map((tag) => (
                    <span key={tag} className="note-tag">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </button>
          ))}

          {notes.length === 0 && <div className="empty">No matching notes.</div>}
        </div>
      </aside>

      <main className="editor-panel">
        {selectedId ? (
          <div className="editor-stack">
            <section className="editor-card editor-meta">
              <div className="editor-meta-grid">
                <label className="meta-field">
                  <span>筆記標題</span>
                  <input
                    value={draft.noteTitle}
                    onChange={(event) => setDraft((current) => ({ ...current, noteTitle: event.target.value }))}
                    placeholder="Untitled note"
                  />
                </label>

                <label className="meta-field">
                  <span>文章標題</span>
                  <input
                    value={draft.articleTitle}
                    onChange={(event) => setDraft((current) => ({ ...current, articleTitle: event.target.value }))}
                    placeholder="Article title"
                  />
                </label>

                <label className="meta-field">
                  <span>文章超連結</span>
                  <div className="inline-field">
                    <input
                      value={draft.articleLink}
                      onChange={(event) => setDraft((current) => ({ ...current, articleLink: event.target.value }))}
                      placeholder="https://..."
                    />
                    <button className="ghost inline-action" type="button" onClick={openArticleLink} disabled={!hasArticleLink}>
                      開啟
                    </button>
                  </div>
                </label>

                <label className="meta-field">
                  <span>標籤</span>
                  <input
                    value={draft.tags}
                    onChange={(event) => setDraft((current) => ({ ...current, tags: event.target.value }))}
                    placeholder="Comma separated"
                  />
                </label>
              </div>
            </section>

            <section className="content-layout">
              <div className="editor-card editor-content">
                <SimpleMDE
                  value={draft.content}
                  onChange={(value) => setDraft((current) => ({ ...current, content: value }))}
                  options={editorOptions}
                />
              </div>
            </section>
          </div>
        ) : (
          <div className="empty-state">
            <h3>Create your first note</h3>
            <p>Use the button on the left to create a note with Markdown editing.</p>
          </div>
        )}
      </main>
    </div>
  );
}
