import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db/client';
import { getAllAlbums, createAlbum } from '@/lib/services/album-service';
import type { ApiError } from '@/types';

export async function GET() {
  try {
    const albumList = await getAllAlbums(db);
    return NextResponse.json({ albums: albumList });
  } catch {
    const err: ApiError = { error: 'INTERNAL_ERROR', message: 'Failed to fetch albums.' };
    return NextResponse.json(err, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json() as { name?: unknown; date?: unknown };

    const name = typeof body.name === 'string' ? body.name.trim() : '';
    const date = typeof body.date === 'string' ? body.date.trim() : '';

    if (!name || name.length > 100) {
      const err: ApiError = {
        error: 'VALIDATION_ERROR',
        message: 'Name must be between 1 and 100 characters.',
        field: 'name',
      };
      return NextResponse.json(err, { status: 422 });
    }

    if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
      const err: ApiError = {
        error: 'VALIDATION_ERROR',
        message: 'Date must be a valid ISO 8601 date (YYYY-MM-DD).',
        field: 'date',
      };
      return NextResponse.json(err, { status: 422 });
    }

    const album = await createAlbum(db, { name, date });
    return NextResponse.json({ album }, { status: 201 });
  } catch {
    const err: ApiError = { error: 'INTERNAL_ERROR', message: 'Failed to create album.' };
    return NextResponse.json(err, { status: 500 });
  }
}
