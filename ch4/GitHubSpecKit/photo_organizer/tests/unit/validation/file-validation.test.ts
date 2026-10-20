import path from 'path';
import fs from 'fs';
import sharp from 'sharp';
import { detectMimeType, validateFile, ValidationError, MAX_SIZE_BYTES } from '@/lib/validation/file-validation';

const FIXTURES = path.join(__dirname, '../../fixtures/images');

async function loadFixture(name: string): Promise<Buffer> {
  const p = path.join(FIXTURES, name);
  if (!fs.existsSync(p)) {
    // Generate on demand
    await sharp({ create: { width: 10, height: 10, channels: 3, background: { r: 255, g: 0, b: 0 } } })
      .jpeg()
      .toFile(path.join(FIXTURES, 'sample.jpg'));
    await sharp({ create: { width: 10, height: 10, channels: 4, background: { r: 0, g: 255, b: 0, alpha: 1 } } })
      .png()
      .toFile(path.join(FIXTURES, 'sample.png'));
    await sharp({ create: { width: 10, height: 10, channels: 3, background: { r: 0, g: 0, b: 255 } } })
      .webp()
      .toFile(path.join(FIXTURES, 'sample.webp'));
    fs.writeFileSync(path.join(FIXTURES, 'invalid.pdf'), '%PDF-1.4 fake content');
  }
  return fs.readFileSync(p);
}

describe('detectMimeType', () => {
  it('identifies JPEG files', async () => {
    const buf = await loadFixture('sample.jpg');
    expect(detectMimeType(buf.slice(0, 12))).toBe('image/jpeg');
  });

  it('identifies PNG files', async () => {
    const buf = await loadFixture('sample.png');
    expect(detectMimeType(buf.slice(0, 12))).toBe('image/png');
  });

  it('identifies WebP files', async () => {
    const buf = await loadFixture('sample.webp');
    expect(detectMimeType(buf.slice(0, 12))).toBe('image/webp');
  });

  it('returns null for PDF files', async () => {
    const buf = await loadFixture('invalid.pdf');
    expect(detectMimeType(buf.slice(0, 12))).toBeNull();
  });

  it('returns null for empty buffer', () => {
    expect(detectMimeType(Buffer.alloc(12))).toBeNull();
  });
});

describe('validateFile', () => {
  it('accepts valid JPEG and returns mime type', async () => {
    const buf = await loadFixture('sample.jpg');
    expect(validateFile(buf.slice(0, 12), buf.length)).toBe('image/jpeg');
  });

  it('throws ValidationError for PDF', async () => {
    const buf = await loadFixture('invalid.pdf');
    expect(() => validateFile(buf.slice(0, 12), buf.length)).toThrow(ValidationError);
  });

  it('throws ValidationError when file exceeds max size', async () => {
    const buf = await loadFixture('sample.jpg');
    expect(() => validateFile(buf.slice(0, 12), MAX_SIZE_BYTES + 1)).toThrow(ValidationError);
  });

  it('throws with field: file', async () => {
    const buf = await loadFixture('invalid.pdf');
    try {
      validateFile(buf.slice(0, 12), buf.length);
      fail('should have thrown');
    } catch (err) {
      expect(err instanceof ValidationError).toBe(true);
      expect((err as ValidationError).field).toBe('file');
    }
  });
});
