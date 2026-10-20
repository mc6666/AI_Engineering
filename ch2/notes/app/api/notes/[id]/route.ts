import { NextRequest, NextResponse } from "next/server";
import { deleteNote, getNote, updateNote } from "@/lib/db";
import type { NoteInput } from "@/lib/types";

export const runtime = "nodejs";

type Params = { params: Promise<{ id: string }> };

function toId(value: string) {
  const id = Number(value);
  return Number.isInteger(id) && id > 0 ? id : null;
}

export async function GET(_request: NextRequest, { params }: Params) {
  const { id: rawId } = await params;
  const id = toId(rawId);
  if (!id) {
    return NextResponse.json({ error: "Invalid note id" }, { status: 400 });
  }

  const note = getNote(id);
  if (!note) {
    return NextResponse.json({ error: "Note not found" }, { status: 404 });
  }

  return NextResponse.json({ note });
}

export async function PUT(request: NextRequest, { params }: Params) {
  const { id: rawId } = await params;
  const id = toId(rawId);
  if (!id) {
    return NextResponse.json({ error: "Invalid note id" }, { status: 400 });
  }

  const body = (await request.json().catch(() => ({}))) as Partial<NoteInput>;
  const note = updateNote(id, {
    noteTitle: body.noteTitle ?? "",
    articleTitle: body.articleTitle ?? "",
    articleLink: body.articleLink ?? "",
    tags: body.tags ?? [],
    content: body.content ?? ""
  });

  if (!note) {
    return NextResponse.json({ error: "Note not found" }, { status: 404 });
  }

  return NextResponse.json({ note });
}

export async function DELETE(_request: NextRequest, { params }: Params) {
  const { id: rawId } = await params;
  const id = toId(rawId);
  if (!id) {
    return NextResponse.json({ error: "Invalid note id" }, { status: 400 });
  }

  const removed = deleteNote(id);
  if (!removed) {
    return NextResponse.json({ error: "Note not found" }, { status: 404 });
  }

  return NextResponse.json({ ok: true });
}
