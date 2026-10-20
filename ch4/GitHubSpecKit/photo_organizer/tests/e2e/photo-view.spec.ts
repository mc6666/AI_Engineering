import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import path from 'path';
import fs from 'fs';
import os from 'os';
import sharp from 'sharp';

async function createSampleJpg(): Promise<string> {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-photo-'));
  const filePath = path.join(dir, 'sample.jpg');
  await sharp({
    create: { width: 100, height: 100, channels: 3, background: { r: 100, g: 150, b: 200 } },
  }).jpeg({ quality: 80 }).toFile(filePath);
  return filePath;
}

test.describe('Accessibility — Album Page', () => {
  test('album page has no WCAG 2.1 AA violations', async ({ page, request }) => {
    const r = await request.post('/api/albums', {
      data: { name: 'A11y Test Album', date: '2026-06-15' },
    });
    const { album } = await r.json();
    await page.goto(`/albums/${album.id}`);
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();
    await request.delete(`/api/albums/${album.id}`);
    expect(results.violations).toEqual([]);
  });
});

test.describe('Photo Tile View', () => {
  let albumId: number;
  let sampleJpgPath: string;

  test.beforeAll(async () => {
    sampleJpgPath = await createSampleJpg();
  });

  test.afterAll(() => {
    fs.rmSync(path.dirname(sampleJpgPath), { recursive: true, force: true });
  });

  test.beforeEach(async ({ request }) => {
    const r = await request.post('/api/albums', {
      data: { name: 'E2E Photo Album', date: '2026-06-15' },
    });
    const { album } = await r.json();
    albumId = album.id;
  });

  test.afterEach(async ({ request }) => {
    await request.delete(`/api/albums/${albumId}`);
  });

  test('album page shows empty state when no photos', async ({ page }) => {
    await page.goto(`/albums/${albumId}`);
    await expect(page.getByText(/no photos yet/i)).toBeVisible();
  });

  test('uploaded photo appears as tile', async ({ page }) => {
    // Upload via the page UI
    await page.goto(`/albums/${albumId}`);

    const [fileChooser] = await Promise.all([
      page.waitForEvent('filechooser'),
      page.getByRole('button', { name: /add photos/i }).first().click(),
    ]);
    await fileChooser.setFiles(sampleJpgPath);

    // Wait for upload to complete — tile should appear
    await expect(page.locator('img[loading="lazy"]').first()).toBeVisible({ timeout: 10000 });
  });

  test('clicking a photo tile opens lightbox', async ({ page }) => {
    // Pre-upload via API
    const jpgBuffer = fs.readFileSync(sampleJpgPath);
    const formData = new FormData();
    formData.append('file', new Blob([jpgBuffer], { type: 'image/jpeg' }), 'sample.jpg');

    await page.request.fetch(`/api/albums/${albumId}/photos`, {
      method: 'POST',
      multipart: { file: { name: 'sample.jpg', mimeType: 'image/jpeg', buffer: jpgBuffer } },
    });

    await page.goto(`/albums/${albumId}`);

    // Click the first tile
    await page.locator('img[loading="lazy"]').first().click();

    // Lightbox should be visible (fixed overlay)
    await expect(page.locator('[role="dialog"], .fixed.inset-0').first()).toBeVisible();
  });

  test('lightbox closes on Escape', async ({ page }) => {
    const jpgBuffer = fs.readFileSync(sampleJpgPath);
    await page.request.fetch(`/api/albums/${albumId}/photos`, {
      method: 'POST',
      multipart: { file: { name: 'sample.jpg', mimeType: 'image/jpeg', buffer: jpgBuffer } },
    });

    await page.goto(`/albums/${albumId}`);
    await page.locator('img[loading="lazy"]').first().click();

    // Press Escape to close
    await page.keyboard.press('Escape');

    // Lightbox should be gone
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();
  });

  test('back button navigates to home', async ({ page }) => {
    await page.goto(`/albums/${albumId}`);
    await page.getByRole('button', { name: /back/i }).click();
    await expect(page).toHaveURL('/');
  });
});
