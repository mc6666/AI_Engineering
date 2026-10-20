import { NextRequest, NextResponse } from 'next/server';
import { eq } from 'drizzle-orm';
import { db } from '@/lib/db/client';
import { photos as photosTable } from '@/lib/db/schema';
import { buildZipStream } from '@/lib/services/export-service';
import type { ExportRequest, EffectType, ApiError } from '@/types';

const VALID_TYPES = new Set<EffectType>([
  'grayscale', 'sepia', 'vintage', 'blur', 'sharpen',
  'brightness', 'contrast', 'saturation',
]);

function validationError(message: string, field?: string): NextResponse<ApiError> {
  return NextResponse.json<ApiError>({ error: 'VALIDATION_ERROR', message, field }, { status: 400 });
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  let body: ExportRequest;
  try {
    body = await request.json() as ExportRequest;
  } catch {
    return validationError('Invalid JSON body');
  }

  const { effects, format, photoIds } = body;

  if (!Array.isArray(photoIds) || photoIds.length === 0) {
    return validationError('photoIds must be a non-empty array', 'photoIds');
  }
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

  const rows = photoIds.map((id: number) =>
    db.select().from(photosTable).where(eq(photosTable.id, id)).get(),
  ).filter(Boolean) as Array<typeof photosTable.$inferSelect>;

  const missing = photoIds.filter((id: number) => !rows.find((r) => r.id === id));
  if (missing.length > 0) {
    return NextResponse.json<ApiError>(
      { error: 'NOT_FOUND', message: `Photos not found: ${missing.join(', ')}` },
      { status: 404 },
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
      'Content-Disposition': 'attachment; filename="photos-export.zip"',
      'Cache-Control': 'no-store',
    },
  });
}
