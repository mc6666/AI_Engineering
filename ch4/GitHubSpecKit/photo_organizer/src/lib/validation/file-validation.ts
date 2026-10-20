export const ALLOWED_MIME_TYPES = [
  'image/jpeg',
  'image/png',
  'image/webp',
  'image/gif',
  'image/heic',
  'image/heif',
] as const;

export type AllowedMimeType = typeof ALLOWED_MIME_TYPES[number];

export const MAX_SIZE_BYTES = 20 * 1024 * 1024; // 20 MB

export class ValidationError extends Error {
  constructor(
    message: string,
    public readonly field: string,
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

/**
 * Detects MIME type from the first 12 bytes (magic bytes).
 * Returns the MIME type string, or null if not a supported image.
 */
export function detectMimeType(header: Buffer): string | null {
  // JPEG: FF D8 FF
  if (header[0] === 0xff && header[1] === 0xd8 && header[2] === 0xff) return 'image/jpeg';

  // PNG: 89 50 4E 47 0D 0A 1A 0A
  if (
    header[0] === 0x89 && header[1] === 0x50 && header[2] === 0x4e && header[3] === 0x47 &&
    header[4] === 0x0d && header[5] === 0x0a && header[6] === 0x1a && header[7] === 0x0a
  ) return 'image/png';

  // GIF: 47 49 46 38
  if (header[0] === 0x47 && header[1] === 0x49 && header[2] === 0x46 && header[3] === 0x38) return 'image/gif';

  // WebP: 52 49 46 46 ?? ?? ?? ?? 57 45 42 50
  if (
    header[0] === 0x52 && header[1] === 0x49 && header[2] === 0x46 && header[3] === 0x46 &&
    header[8] === 0x57 && header[9] === 0x45 && header[10] === 0x42 && header[11] === 0x50
  ) return 'image/webp';

  // HEIC/HEIF: ftyp box at offset 4: 'heic' or 'heif' or 'mif1' or 'msf1'
  if (header.length >= 12) {
    const ftyp = header.slice(4, 8).toString('ascii');
    const brand = header.slice(8, 12).toString('ascii');
    if (ftyp === 'ftyp') {
      if (['heic', 'heix', 'hevc', 'hevx'].includes(brand)) return 'image/heic';
      if (['heif', 'mif1', 'msf1'].includes(brand)) return 'image/heif';
    }
  }

  return null;
}

export function validateFile(header: Buffer, sizeBytes: number): AllowedMimeType {
  if (sizeBytes > MAX_SIZE_BYTES) {
    throw new ValidationError(
      `File size ${sizeBytes} bytes exceeds the 20 MB limit.`,
      'file',
    );
  }

  const mimeType = detectMimeType(header);
  if (!mimeType || !(ALLOWED_MIME_TYPES as readonly string[]).includes(mimeType)) {
    throw new ValidationError(
      'File type is not a supported image format. Supported types: JPEG, PNG, WebP, GIF, HEIC.',
      'file',
    );
  }

  return mimeType as AllowedMimeType;
}
