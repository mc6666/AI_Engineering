import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db/client';
import { getThumbnailPath, getPhotoById } from '@/lib/services/photo-service';
import fs from 'fs';
import type { ApiError } from '@/types';

const DATA_DIR = process.env.DATA_DIR ?? './data';

type Params = { params: Promise<{ id: string }> };

export async function GET(_req: NextRequest, { params }: Params) {
  const { id } = await params;
  const photoId = parseInt(id, 10);
  if (isNaN(photoId)) return notFound();

  const photo = getPhotoById(db, photoId);
  if (!photo) return notFound();

  const thumbPath = getThumbnailPath(db, photoId, DATA_DIR);
  if (!thumbPath || !fs.existsSync(thumbPath)) return notFound();

  const fileBuffer = fs.readFileSync(thumbPath);

  return new NextResponse(fileBuffer, {
    status: 200,
    headers: {
      'Content-Type': 'image/jpeg',
      'Content-Length': String(fileBuffer.length),
      'Cache-Control': 'public, max-age=31536000, immutable',
    },
  });
}

function notFound() {
  const err: ApiError = { error: 'NOT_FOUND', message: 'Photo not found.' };
  return NextResponse.json(err, { status: 404 });
}
