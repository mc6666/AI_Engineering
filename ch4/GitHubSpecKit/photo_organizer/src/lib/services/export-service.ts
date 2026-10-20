import fs from 'fs';
import path from 'path';
import type { Readable } from 'stream';
import type { Archiver } from 'archiver';
import { applyEffects } from '@/lib/services/effect-service';
import type { EffectChain, OutputFormat } from '@/types';

// eslint-disable-next-line @typescript-eslint/no-require-imports, @typescript-eslint/no-explicit-any
const createArchive: (format: string, opts?: object) => Archiver = require('archiver') as any;

const DATA_DIR = process.env.DATA_DIR ?? './data';

interface PhotoEntry {
  id: number;
  filepath: string;
  filename: string;
}

export function buildZipStream(
  photos: PhotoEntry[],
  chain: EffectChain,
  format: OutputFormat,
  dataDir: string = DATA_DIR,
): Readable {
  if (photos.length === 0) {
    throw new Error('No photos to export');
  }

  const archive = createArchive('zip', { zlib: { level: 6 } });
  const ext = format === 'png' ? 'png' : 'jpg';

  (async () => {
    for (let i = 0; i < photos.length; i++) {
      const { filepath, filename } = photos[i];
      try {
        const absPath = path.resolve(path.join(dataDir, filepath));
        const base = path.resolve(dataDir);
        if (!absPath.startsWith(base)) continue;

        const source = fs.readFileSync(absPath);
        const processed = await applyEffects(source, chain, format);

        const baseName = path.basename(filename, path.extname(filename));
        const entryName = `${String(i + 1).padStart(3, '0')}-${baseName}.${ext}`;
        archive.append(processed, { name: entryName });
      } catch {
        // skip unreadable photos rather than aborting the entire export
      }
    }
    await archive.finalize();
  })().catch((err: Error) => archive.emit('error', err));

  return archive as unknown as Readable;
}
