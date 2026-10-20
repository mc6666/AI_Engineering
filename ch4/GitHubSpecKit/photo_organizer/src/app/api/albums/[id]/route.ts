import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db/client';
import { getAlbumById, updateAlbum, deleteAlbum } from '@/lib/services/album-service';
import type { ApiError } from '@/types';

const DATA_DIR = process.env.DATA_DIR ?? './data';

type Params = { params: Promise<{ id: string }> };

export async function GET(_req: NextRequest, { params }: Params) {
  const { id } = await params;
  const albumId = parseInt(id, 10);
  if (isNaN(albumId)) return notFound();

  const result = await getAlbumById(db, albumId);
  if (!result) return notFound();

  return NextResponse.json({ album: result, photos: result.photos });
}

export async function PUT(request: NextRequest, { params }: Params) {
  const { id } = await params;
  const albumId = parseInt(id, 10);
  if (isNaN(albumId)) return notFound();

  const body = await request.json() as { name?: unknown; date?: unknown };
  const patch: Partial<{ name: string; date: string }> = {};

  if (body.name !== undefined) {
    const name = String(body.name).trim();
    if (!name || name.length > 100) {
      const err: ApiError = { error: 'VALIDATION_ERROR', message: 'Name must be 1–100 characters.', field: 'name' };
      return NextResponse.json(err, { status: 422 });
    }
    patch.name = name;
  }

  if (body.date !== undefined) {
    const date = String(body.date).trim();
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
      const err: ApiError = { error: 'VALIDATION_ERROR', message: 'Date must be YYYY-MM-DD.', field: 'date' };
      return NextResponse.json(err, { status: 422 });
    }
    patch.date = date;
  }

  const updated = await updateAlbum(db, albumId, patch);
  if (!updated) return notFound();
  return NextResponse.json({ album: updated });
}

export async function DELETE(_req: NextRequest, { params }: Params) {
  const { id } = await params;
  const albumId = parseInt(id, 10);
  if (isNaN(albumId)) return notFound();

  const deleted = await deleteAlbum(db, albumId, DATA_DIR);
  if (!deleted) return notFound();
  return new NextResponse(null, { status: 204 });
}

function notFound() {
  const err: ApiError = { error: 'NOT_FOUND', message: 'Album not found.' };
  return NextResponse.json(err, { status: 404 });
}
