import sharp from 'sharp';
import type { EffectChain, OutputFormat } from '@/types';

const KNOWN_TYPES = new Set([
  'grayscale', 'sepia', 'vintage', 'blur', 'sharpen',
  'brightness', 'contrast', 'saturation',
]);

const SEPIA_MATRIX: sharp.Matrix3x3 = [
  [0.393, 0.769, 0.189],
  [0.349, 0.686, 0.168],
  [0.272, 0.534, 0.131],
];

function applyEffect(instance: sharp.Sharp, type: string, intensity: number): sharp.Sharp {
  switch (type) {
    case 'grayscale':
      return instance.grayscale();
    case 'sepia':
      return instance.recomb(SEPIA_MATRIX);
    case 'vintage':
      return instance
        .recomb(SEPIA_MATRIX)
        .modulate({ brightness: 0.9, saturation: 0.8 })
        .linear(1.1, 0);
    case 'blur':
      return instance.blur(Math.max(0.3, intensity * 0.08));
    case 'sharpen':
      return instance.sharpen({ sigma: 1 + intensity * 0.03, m1: 1.5, m2: 0.7 });
    case 'brightness':
      return instance.modulate({ brightness: 0.5 + intensity * 0.015 });
    case 'contrast': {
      const factor = 0.5 + intensity * 0.015;
      return instance.linear(factor, -(128 * (factor - 1)));
    }
    case 'saturation':
      return instance.modulate({ saturation: intensity / 33.3 });
    default:
      throw new Error(`Unknown effect type: ${type}`);
  }
}

export async function applyEffects(
  source: Buffer,
  chain: EffectChain,
  format: OutputFormat,
): Promise<Buffer> {
  if (chain.length > 5) {
    throw new Error('effects must have at most 5 items');
  }

  for (const { type } of chain) {
    if (!KNOWN_TYPES.has(type)) {
      throw new Error(`Unknown effect type: ${type}`);
    }
  }

  let instance = sharp(source);
  for (const { type, intensity } of chain) {
    instance = applyEffect(instance, type, intensity);
  }

  if (format === 'png') {
    return instance.png({ compressionLevel: 6 }).toBuffer();
  }
  return instance.jpeg({ quality: 90, progressive: true }).toBuffer();
}
