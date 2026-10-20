import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db/client';
import { reorderAlbum } from '@/lib/services/album-service';
import type { ApiError } from '@/types';

type Params = { params: Promise<{ id: string }> };

export async function POST(request: NextRequest, { params }: Params) {
  const { id } = await params;
  const albumId = parseInt(id, 10);
  if (isNaN(albumId)) {
    const err: ApiError = { error: 'NOT_FOUND', message: 'Album not found.' };
    return NextResponse.json(err, { status: 404 });
  }

  const body = await request.json() as { predecessorOrder?: unknown; successorOrder?: unknown };

  if (body.predecessorOrder === undefined && body.successorOrder === undefined) {
    const err: ApiError = {
      error: 'VALIDATION_ERROR',
      message: 'At least one of predecessorOrder or successorOrder must be provided.',
    };
    return NextResponse.json(err, { status: 422 });
  }

  const opts: { predecessorOrder?: number; successorOrder?: number } = {};
  if (typeof body.predecessorOrder === 'number') opts.predecessorOrder = body.predecessorOrder;
  if (typeof body.successorOrder === 'number') opts.successorOrder = body.successorOrder;

  try {
    const album = await reorderAlbum(db, albumId, opts);
    return NextResponse.json({ album });
  } catch {
    const err: ApiError = { error: 'NOT_FOUND', message: 'Album not found.' };
    return NextResponse.json(err, { status: 404 });
  }
}
