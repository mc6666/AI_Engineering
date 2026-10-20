import sharp from 'sharp';
import path from 'path';
import fs from 'fs';

const FIXTURES_DIR = path.join(__dirname, '../tests/fixtures/images');

async function main() {
  fs.mkdirSync(FIXTURES_DIR, { recursive: true });

  await sharp({
    create: { width: 100, height: 100, channels: 3, background: { r: 255, g: 100, b: 50 } },
  }).jpeg({ quality: 80 }).toFile(path.join(FIXTURES_DIR, 'sample.jpg'));

  await sharp({
    create: { width: 100, height: 100, channels: 4, background: { r: 50, g: 150, b: 255, alpha: 1 } },
  }).png().toFile(path.join(FIXTURES_DIR, 'sample.png'));

  await sharp({
    create: { width: 100, height: 100, channels: 3, background: { r: 100, g: 200, b: 80 } },
  }).webp({ quality: 80 }).toFile(path.join(FIXTURES_DIR, 'sample.webp'));

  await sharp({
    create: { width: 100, height: 100, channels: 3, background: { r: 200, g: 50, b: 200 } },
  }).gif().toFile(path.join(FIXTURES_DIR, 'sample.gif'));

  // Invalid file: PDF header magic bytes
  fs.writeFileSync(path.join(FIXTURES_DIR, 'invalid.pdf'), '%PDF-1.4 fake pdf content');

  console.log('Test fixtures generated in', FIXTURES_DIR);
}

main().catch(console.error);
