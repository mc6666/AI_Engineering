import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db/client';
import { removePhoto } from '@/lib/services/photo-service';
import type { ApiError } from '@/types';

const DATA_DIR = process.env.DATA_DIR ?? './data';

type Params = { params: Promise<{ id: string }> };

export async function DELETE(_req: NextRequest, { params }: Params) {
  const { id } = await params;
  const photoId = parseInt(id, 10);
  if (isNaN(photoId)) return notFound();

  const deleted = removePhoto(db, photoId, DATA_DIR);
  if (!deleted) return notFound();
  return new NextResponse(null, { status: 204 });
}

function notFound() {
  const err: ApiError = { error: 'NOT_FOUND', message: 'Photo not found.' };
  return NextResponse.json(err, { status: 404 });
}
