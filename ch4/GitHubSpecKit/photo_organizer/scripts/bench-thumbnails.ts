import sharp from 'sharp';
import os from 'os';
import path from 'path';
import fs from 'fs';

const COUNT = 200;
const THUMB_SIZE = 400;
const OUT_DIR = path.join(os.tmpdir(), 'photo-organizer-bench');

async function run() {
  fs.mkdirSync(OUT_DIR, { recursive: true });

  // Create a source image buffer once
  const sourceBuffer = await sharp({
    create: { width: 2000, height: 1500, channels: 3, background: { r: 128, g: 100, b: 80 } },
  }).jpeg({ quality: 90 }).toBuffer();

  console.log(`Generating ${COUNT} thumbnails (${THUMB_SIZE}×${THUMB_SIZE} JPEG)…`);

  const start = performance.now();

  for (let i = 0; i < COUNT; i++) {
    await sharp(sourceBuffer)
      .resize(THUMB_SIZE, THUMB_SIZE, { fit: 'cover' })
      .jpeg({ quality: 80 })
      .toFile(path.join(OUT_DIR, `thumb-${i}.jpg`));
  }

  const elapsed = (performance.now() - start) / 1000;
  const tps = COUNT / elapsed;

  console.log(`\nResults:`);
  console.log(`  Total time : ${elapsed.toFixed(2)} s`);
  console.log(`  Throughput : ${tps.toFixed(1)} thumbnails/s`);

  if (tps < 100) {
    console.error(`\n❌ FAIL: Throughput ${tps.toFixed(1)}/s is below the required 100/s threshold.`);
    process.exit(1);
  } else {
    console.log(`\n✅ PASS: Throughput ${tps.toFixed(1)}/s meets the ≥ 100/s requirement.`);
  }

  fs.rmSync(OUT_DIR, { recursive: true, force: true });
}

run().catch((err) => { console.error(err); process.exit(1); });
