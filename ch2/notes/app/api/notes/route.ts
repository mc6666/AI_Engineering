import { NextRequest, NextResponse } from "next/server";
import { createNote, listNotes } from "@/lib/db";

export const runtime = "nodejs";

export function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const query = searchParams.get("q") ?? "";
  return NextResponse.json({ notes: listNotes(query) });
}

export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => ({}));
  const note = createNote(body);
  return NextResponse.json({ note }, { status: 201 });
}
