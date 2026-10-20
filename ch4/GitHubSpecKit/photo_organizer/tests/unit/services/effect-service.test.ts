import path from 'path';
import fs from 'fs';
import sharp from 'sharp';
import { applyEffects } from '@/lib/services/effect-service';
import type { EffectChain, OutputFormat } from '@/types';

const FIXTURES = path.join(__dirname, '../../fixtures/images');

async function getFixture(name: string): Promise<Buffer> {
  const p = path.join(FIXTURES, name);
  if (!fs.existsSync(p)) {
    fs.mkdirSync(FIXTURES, { recursive: true });
    await sharp({ create: { width: 100, height: 100, channels: 3, background: { r: 200, g: 100, b: 50 } } })
      .jpeg({ quality: 80 }).toFile(path.join(FIXTURES, 'sample.jpg'));
    await sharp({ create: { width: 100, height: 100, channels: 4, background: { r: 50, g: 150, b: 255, alpha: 1 } } })
      .png().toFile(path.join(FIXTURES, 'sample.png'));
  }
  return fs.readFileSync(p);
}

async function isValidImage(buf: Buffer): Promise<boolean> {
  try {
    await sharp(buf).metadata();
    return true;
  } catch {
    return false;
  }
}

describe('applyEffects — each effect type', () => {
  let jpgSource: Buffer;

  beforeAll(async () => {
    jpgSource = await getFixture('sample.jpg');
  });

  const singleEffectCases: Array<[EffectChain[0]['type'], number]> = [
    ['grayscale', 100],
    ['sepia', 100],
    ['vintage', 50],
    ['blur', 40],
    ['sharpen', 60],
    ['brightness', 70],
    ['contrast', 50],
    ['saturation', 80],
  ];

  for (const [type, intensity] of singleEffectCases) {
    it(`applies ${type} effect and returns a valid JPEG buffer`, async () => {
      const chain: EffectChain = [{ type, intensity }];
      const result = await applyEffects(jpgSource, chain, 'jpeg');
      expect(Buffer.isBuffer(result)).toBe(true);
      expect(result.length).toBeGreaterThan(0);
      expect(await isValidImage(result)).toBe(true);
      const meta = await sharp(result).metadata();
      expect(meta.format).toBe('jpeg');
    });
  }

  it('outputs PNG when format is png', async () => {
    const result = await applyEffects(jpgSource, [{ type: 'grayscale', intensity: 100 }], 'png');
    const meta = await sharp(result).metadata();
    expect(meta.format).toBe('png');
  });
});

describe('applyEffects — chain behaviour', () => {
  let jpgSource: Buffer;

  beforeAll(async () => {
    jpgSource = await getFixture('sample.jpg');
  });

  it('applies a chain of 5 effects and returns a valid image', async () => {
    const chain: EffectChain = [
      { type: 'brightness', intensity: 60 },
      { type: 'contrast', intensity: 50 },
      { type: 'saturation', intensity: 40 },
      { type: 'blur', intensity: 20 },
      { type: 'sharpen', intensity: 30 },
    ];
    const result = await applyEffects(jpgSource, chain, 'jpeg');
    expect(await isValidImage(result)).toBe(true);
  });

  it('empty chain returns a valid image in the requested format', async () => {
    const result = await applyEffects(jpgSource, [], 'png');
    const meta = await sharp(result).metadata();
    expect(meta.format).toBe('png');
    expect(result.length).toBeGreaterThan(0);
  });

  it('throws when chain length exceeds 5', async () => {
    const chain: EffectChain = [
      { type: 'blur', intensity: 10 },
      { type: 'blur', intensity: 20 },
      { type: 'blur', intensity: 30 },
      { type: 'blur', intensity: 40 },
      { type: 'blur', intensity: 50 },
      { type: 'blur', intensity: 60 },
    ] as unknown as EffectChain;
    await expect(applyEffects(jpgSource, chain, 'jpeg')).rejects.toThrow('effects must have at most 5 items');
  });

  it('throws when an unknown effect type is provided', async () => {
    const chain = [{ type: 'oil_paint' as EffectChain[0]['type'], intensity: 50 }];
    await expect(applyEffects(jpgSource, chain, 'jpeg')).rejects.toThrow('Unknown effect type');
  });
});
