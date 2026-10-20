import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import { db } from '@/lib/db/client';
import { getImagePath } from '@/lib/services/photo-service';
import { applyEffects } from '@/lib/services/effect-service';
import type { ProcessRequest, EffectType, ApiError } from '@/types';

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
  const photoId = Number(id);

  if (!Number.isInteger(photoId) || photoId <= 0) {
    return NextResponse.json<ApiError>({ error: 'NOT_FOUND', message: 'Photo not found' }, { status: 404 });
  }

  let body: ProcessRequest;
  try {
    body = await request.json() as ProcessRequest;
  } catch {
    return validationError('Invalid JSON body');
  }

  const { effects, format } = body;

  if (!Array.isArray(effects)) {
    return validationError('effects must be an array', 'effects');
  }
  if (effects.length > 5) {
    return validationError('effects must have at most 5 items', 'effects');
  }
  for (const e of effects) {
    if (!VALID_TYPES.has(e?.type)) {
      return validationError(`Unknown effect type: ${e?.type}`, 'effects');
    }
    if (typeof e.intensity !== 'number' || e.intensity < 0 || e.intensity > 100) {
      return validationError('intensity must be an integer between 0 and 100', 'effects');
    }
  }
  if (format !== 'jpeg' && format !== 'png') {
    return validationError('format must be jpeg or png', 'format');
  }

  const imagePath = getImagePath(db, photoId);
  if (!imagePath) {
    return NextResponse.json<ApiError>({ error: 'NOT_FOUND', message: 'Photo not found' }, { status: 404 });
  }

  try {
    const source = fs.readFileSync(imagePath);
    const processed = await applyEffects(source, effects, format);
    const ext = format === 'png' ? 'png' : 'jpg';
    const contentType = format === 'png' ? 'image/png' : 'image/jpeg';

    return new NextResponse(new Uint8Array(processed), {
      status: 200,
      headers: {
        'Content-Type': contentType,
        'Content-Disposition': `attachment; filename="photo-${photoId}-processed.${ext}"`,
        'Cache-Control': 'no-store',
      },
    });
  } catch {
    return NextResponse.json<ApiError>({ error: 'INTERNAL_ERROR', message: 'Image processing failed' }, { status: 500 });
  }
}
