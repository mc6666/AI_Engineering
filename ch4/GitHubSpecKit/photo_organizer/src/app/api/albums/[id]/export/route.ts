import { NextRequest, NextResponse } from 'next/server';
import { eq } from 'drizzle-orm';
import { db } from '@/lib/db/client';
import { albums as albumsTable, photos as photosTable } from '@/lib/db/schema';
import { buildZipStream } from '@/lib/services/export-service';
import type { ExportRequest, EffectType, ApiError } from '@/types';

const VALID_TYPES = new Set<EffectType>([
  'grayscale', 'sepia', 'vintage', 'blur', 'sharpen',
  'brightness', 'contrast', 'saturation',
]);

function validationError(message: string, field?: string): NextResponse<ApiError> {
  return NextResponse.json<ApiError>({ error: 'VALIDATION_ERROR', message, field }, { status: 400 });
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
): Promise<NextResponse> {
  const { id } = await params;
  const albumId = Number(id);

  if (!Number.isInteger(albumId) || albumId <= 0) {
    return NextResponse.json<ApiError>({ error: 'NOT_FOUND', message: 'Album not found' }, { status: 404 });
  }

  let body: ExportRequest;
  try {
    body = await request.json() as ExportRequest;
  } catch {
    return validationError('Invalid JSON body');
  }

  const { effects, format } = body;

  if (!Array.isArray(effects) || effects.length > 5) {
    return validationError('effects must be an array of at most 5 items', 'effects');
  }
  for (const e of effects) {
    if (!VALID_TYPES.has(e?.type)) {
      return validationError(`Unknown effect type: ${e?.type}`, 'effects');
    }
  }
  if (format !== 'jpeg' && format !== 'png') {
    return validationError('format must be jpeg or png', 'format');
  }

  const album = db.select().from(albumsTable).where(eq(albumsTable.id, albumId)).get();
  if (!album) {
    return NextResponse.json<ApiError>({ error: 'NOT_FOUND', message: 'Album not found' }, { status: 404 });
  }

  const rows = db
    .select()
    .from(photosTable)
    .where(eq(photosTable.album_id, albumId))
    .orderBy(photosTable.display_order)
    .all();

  if (rows.length === 0) {
    return NextResponse.json<ApiError>(
      { error: 'VALIDATION_ERROR', message: 'Album has no photos to export' },
      { status: 422 },
    );
  }

  const photoList = rows.map((r) => ({ id: r.id, filepath: r.filepath, filename: r.filename }));
  const stream = buildZipStream(photoList, effects, format);

  const { Readable } = await import('stream');
  const webStream = Readable.toWeb(stream as import('stream').Readable) as ReadableStream;

  return new NextResponse(webStream, {
    status: 200,
    headers: {
      'Content-Type': 'application/zip',
      'Content-Disposition': `attachment; filename="album-${albumId}-export.zip"`,
      'Cache-Control': 'no-store',
    },
  });
}
