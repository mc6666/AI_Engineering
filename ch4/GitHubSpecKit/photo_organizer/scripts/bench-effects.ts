import sharp from 'sharp';
import type { EffectType } from '../src/types';

const COUNT = 100;
const EFFECT_TYPES: EffectType[] = [
  'grayscale', 'sepia', 'vintage', 'blur', 'sharpen',
  'brightness', 'contrast', 'saturation',
];
const THRESHOLD = 10; // photos/s

function buildPipeline(instance: sharp.Sharp, type: EffectType, intensity: number): sharp.Sharp {
  switch (type) {
    case 'grayscale':
      return instance.grayscale();
    case 'sepia':
      return instance.recomb([
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131],
      ]);
    case 'vintage': {
      const sepiaMatrix: sharp.Matrix3x3 = [
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131],
      ];
      return instance
        .recomb(sepiaMatrix)
        .modulate({ brightness: 0.9, saturation: 0.8 })
        .linear(1.1, 0);
    }
    case 'blur':
      return instance.blur(Math.max(0.3, intensity * 0.08));
    case 'sharpen':
      return instance.sharpen({ sigma: 1 + intensity * 0.03, m1: 1.5, m2: 0.7 });
    case 'brightness':
      return instance.modulate({ brightness: 0.5 + intensity * 0.015 });
    case 'contrast':
      return instance.linear(0.5 + intensity * 0.015, -(128 * (intensity * 0.015 - 0.5)));
    case 'saturation':
      return instance.modulate({ saturation: intensity / 33.3 });
  }
}

async function benchEffect(sourceBuffer: Buffer, type: EffectType): Promise<number> {
  const start = performance.now();
  for (let i = 0; i < COUNT; i++) {
    await buildPipeline(sharp(sourceBuffer), type, 50).jpeg({ quality: 90 }).toBuffer();
  }
  const elapsed = (performance.now() - start) / 1000;
  return COUNT / elapsed;
}

async function run() {
  const sourceBuffer = await sharp({
    create: { width: 800, height: 600, channels: 3, background: { r: 128, g: 100, b: 80 } },
  }).jpeg({ quality: 90 }).toBuffer();

  console.log(`Benchmarking ${COUNT} photos per effect type…\n`);

  let allPass = true;
  for (const type of EFFECT_TYPES) {
    const tps = await benchEffect(sourceBuffer, type);
    const pass = tps >= THRESHOLD;
    if (!pass) allPass = false;
    const icon = pass ? '✅' : '❌';
    console.log(`  ${icon} ${type.padEnd(12)}: ${tps.toFixed(1)} photos/s${pass ? '' : ` (below ${THRESHOLD})`}`);
  }

  console.log('');
  if (!allPass) {
    console.error(`❌ FAIL: One or more effects are below the ${THRESHOLD} photos/s threshold.`);
    process.exit(1);
  }
  console.log(`✅ PASS: All effects meet the ≥ ${THRESHOLD} photos/s requirement.`);
}

run().catch((err) => { console.error(err); process.exit(1); });
