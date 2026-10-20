import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Photo Effects Panel — US1: Apply Special Effects', () => {
  let albumId: number;
  let photoId: number;

  test.beforeAll(async ({ request }) => {
    const albumRes = await request.post('/api/albums', {
      data: { name: 'Effects Test Album', date: '2026-06-17' },
    });
    const { album } = await albumRes.json();
    albumId = album.id;

    const fixture = Buffer.from(
      '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8U'
      + 'HRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDB'
      + 'gNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjI'
      + 'yMjIyMjL/wAARCAAKAAoDASIAAhEBAxEB/8QAFgABAQEAAAAAAAAAAAAAAAAABgUE/8QA'
      + 'IRAAAQMEBAMAAAAAAAAAAAAAAAECBBEDBBIUITH/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8'
      + 'QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8Amk61LUFQhNQ2j0YKy7cZSO'
      + 'WA8OoxRWk7NjwSAAAAAAAAA//9k=',
      'base64',
    );

    const form = new FormData();
    const blob = new Blob([fixture], { type: 'image/jpeg' });
    form.append('file', blob, 'sample.jpg');

    const photoRes = await request.post(`/api/albums/${albumId}/photos`, {
      multipart: {
        file: { name: 'sample.jpg', mimeType: 'image/jpeg', buffer: fixture },
      },
    });
    const { photo } = await photoRes.json();
    photoId = photo.id;
  });

  test.afterAll(async ({ request }) => {
    await request.delete(`/api/albums/${albumId}`);
  });

  test('effects panel opens with 8 effect tiles', async ({ page }) => {
    await page.goto(`/albums/${albumId}`);
    await page.waitForLoadState('networkidle');

    await page.locator('[data-testid="photo-tile"]').first().click();
    await expect(page.locator('[role="dialog"][aria-label*="Photo"]')).toBeVisible();

    await page.locator('[data-testid="effects-toggle"]').click();
    await expect(page.locator('[data-testid="effects-panel"]')).toBeVisible();

    const tiles = page.locator('[data-testid="effect-tile"]');
    await expect(tiles).toHaveCount(8);
  });

  test('selecting grayscale applies CSS filter to preview', async ({ page }) => {
    await page.goto(`/albums/${albumId}`);
    await page.waitForLoadState('networkidle');

    await page.locator('[data-testid="photo-tile"]').first().click();
    await page.locator('[data-testid="effects-toggle"]').click();

    await page.locator('[data-testid="effect-tile"][data-effect="grayscale"]').click();

    const preview = page.locator('[data-testid="effect-preview-img"]');
    await expect(preview).toBeVisible();
    const filter = await preview.evaluate((el) => getComputedStyle(el).filter);
    expect(filter).toContain('grayscale');
  });

  test('intensity slider updates the CSS filter', async ({ page }) => {
    await page.goto(`/albums/${albumId}`);
    await page.waitForLoadState('networkidle');

    await page.locator('[data-testid="photo-tile"]').first().click();
    await page.locator('[data-testid="effects-toggle"]').click();
    await page.locator('[data-testid="effect-tile"][data-effect="grayscale"]').click();

    const slider = page.locator('[data-testid="intensity-slider"]');
    await slider.fill('50');

    const preview = page.locator('[data-testid="effect-preview-img"]');
    const filter = await preview.evaluate((el) => getComputedStyle(el).filter);
    expect(filter).toContain('grayscale');
  });

  test('Reset clears all effects', async ({ page }) => {
    await page.goto(`/albums/${albumId}`);
    await page.waitForLoadState('networkidle');

    await page.locator('[data-testid="photo-tile"]').first().click();
    await page.locator('[data-testid="effects-toggle"]').click();
    await page.locator('[data-testid="effect-tile"][data-effect="sepia"]').click();
    await page.locator('[data-testid="reset-effects"]').click();

    const preview = page.locator('[data-testid="effect-preview-img"]');
    const filter = await preview.evaluate((el) => (el as HTMLElement).style.filter);
    expect(['', 'none']).toContain(filter);
  });

  test('effects panel passes axe accessibility audit', async ({ page }) => {
    await page.goto(`/albums/${albumId}`);
    await page.waitForLoadState('networkidle');

    await page.locator('[data-testid="photo-tile"]').first().click();
    await page.locator('[data-testid="effects-toggle"]').click();

    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toHaveLength(0);
  });
});

test.describe('Photo Download — US2: Single Photo Download', () => {
  let albumId: number;

  test.beforeAll(async ({ request }) => {
    const albumRes = await request.post('/api/albums', {
      data: { name: 'Download Test Album', date: '2026-06-17' },
    });
    const { album } = await albumRes.json();
    albumId = album.id;

    const fixture = Buffer.from(
      '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8U'
      + 'HRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDB'
      + 'gNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjI'
      + 'yMjIyMjL/wAARCAAKAAoDASIAAhEBAxEB/8QAFgABAQEAAAAAAAAAAAAAAAAABgUE/8QA'
      + 'IRAAAQMEBAMAAAAAAAAAAAAAAAECBBEDBBIUITH/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8'
      + 'QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8Amk61LUFQhNQ2j0YKy7cZSO'
      + 'WA8OoxRWk7NjwSAAAAAAAAA//9k=',
      'base64',
    );

    await request.post(`/api/albums/${albumId}/photos`, {
      multipart: {
        file: { name: 'dl-test.jpg', mimeType: 'image/jpeg', buffer: fixture },
      },
    });
  });

  test.afterAll(async ({ request }) => {
    await request.delete(`/api/albums/${albumId}`);
  });

  test('Download button triggers file save', async ({ page }) => {
    await page.goto(`/albums/${albumId}`);
    await page.waitForLoadState('networkidle');

    await page.locator('[data-testid="photo-tile"]').first().click();
    await page.locator('[data-testid="effects-toggle"]').click();
    await page.locator('[data-testid="effect-tile"][data-effect="grayscale"]').click();

    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.locator('[data-testid="download-photo"]').click(),
    ]);

    expect(download.suggestedFilename()).toMatch(/photo-\d+-processed\.(jpg|png)/);
  });
});

test.describe('Batch Export — US3: Export Album as ZIP', () => {
  let albumId: number;

  test.beforeAll(async ({ request }) => {
    const albumRes = await request.post('/api/albums', {
      data: { name: 'Export Test Album', date: '2026-06-17' },
    });
    const { album } = await albumRes.json();
    albumId = album.id;

    const fixture = Buffer.from(
      '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8U'
      + 'HRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDB'
      + 'gNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjI'
      + 'yMjIyMjL/wAARCAAKAAoDASIAAiEBAxEB/8QAFgABAQEAAAAAAAAAAAAAAAAABgUE/8QA'
      + 'IRAAAQMEBAMAAAAAAAAAAAAAAAECBBEDBBIUITH/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8'
      + 'QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8Amk61LUFQhNQ2j0YKy7cZSO'
      + 'WA8OoxRWk7NjwSAAAAAAAAA//9k=',
      'base64',
    );

    for (let i = 0; i < 3; i++) {
      await request.post(`/api/albums/${albumId}/photos`, {
        multipart: {
          file: { name: `export-test-${i}.jpg`, mimeType: 'image/jpeg', buffer: fixture },
        },
      });
    }
  });

  test.afterAll(async ({ request }) => {
    await request.delete(`/api/albums/${albumId}`);
  });

  test('Export Album button downloads a ZIP file', async ({ page }) => {
    await page.goto(`/albums/${albumId}`);
    await page.waitForLoadState('networkidle');

    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.locator('[data-testid="export-album"]').click(),
    ]);

    expect(download.suggestedFilename()).toMatch(/album-\d+-export\.zip/);
  });
});
