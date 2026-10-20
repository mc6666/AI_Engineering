import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db/client';
import { getAlbumById } from '@/lib/services/album-service';
import { addPhoto } from '@/lib/services/photo-service';
import { ValidationError } from '@/lib/validation/file-validation';
import type { ApiError } from '@/types';

const DATA_DIR = process.env.DATA_DIR ?? './data';
const MAX_SIZE = parseInt(process.env.MAX_UPLOAD_SIZE_MB ?? '20', 10) * 1024 * 1024;

type Params = { params: Promise<{ id: string }> };

export async function POST(request: NextRequest, { params }: Params) {
  const { id } = await params;
  const albumId = parseInt(id, 10);
  if (isNaN(albumId)) return notFound();

  const album = await getAlbumById(db, albumId);
  if (!album) return notFound();

  let formData: FormData;
  try {
    formData = await request.formData();
  } catch {
    const err: ApiError = { error: 'VALIDATION_ERROR', message: 'Invalid multipart form data.', field: 'file' };
    return NextResponse.json(err, { status: 422 });
  }

  const file = formData.get('file') as File | null;
  if (!file) {
    const err: ApiError = { error: 'VALIDATION_ERROR', message: 'No file provided.', field: 'file' };
    return NextResponse.json(err, { status: 422 });
  }

  if (file.size > MAX_SIZE) {
    const err: ApiError = { error: 'PAYLOAD_TOO_LARGE', message: `File exceeds the ${MAX_SIZE / 1024 / 1024} MB limit.` };
    return NextResponse.json(err, { status: 413 });
  }

  const buffer = Buffer.from(await file.arrayBuffer());

  try {
    const photo = await addPhoto(db, albumId, buffer, file.name, DATA_DIR);
    return NextResponse.json({ photo }, { status: 201 });
  } catch (err) {
    if (err instanceof ValidationError) {
      const apiErr: ApiError = { error: 'VALIDATION_ERROR', message: err.message, field: 'file' };
      return NextResponse.json(apiErr, { status: 422 });
    }
    const apiErr: ApiError = { error: 'INTERNAL_ERROR', message: 'Failed to process photo.' };
    return NextResponse.json(apiErr, { status: 500 });
  }
}

function notFound() {
  const err: ApiError = { error: 'NOT_FOUND', message: 'Album not found.' };
  return NextResponse.json(err, { status: 404 });
}
