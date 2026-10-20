import { test, expect } from '@playwright/test';

test.describe('Performance', () => {
  test('home page loads within 3 seconds', async ({ page }) => {
    // Create a few albums
    const albumIds: number[] = [];
    for (let i = 0; i < 5; i++) {
      const r = await page.request.post('/api/albums', {
        data: { name: `Perf Album ${i}`, date: `2026-0${(i % 9) + 1}-01` },
      });
      const { album } = await r.json();
      albumIds.push(album.id);
    }

    const start = Date.now();
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    const elapsed = Date.now() - start;

    expect(elapsed).toBeLessThan(3000);

    // Verify albums are visible
    await expect(page.getByText('Perf Album 0')).toBeVisible();

    for (const id of albumIds) {
      await page.request.delete(`/api/albums/${id}`);
    }
  });

  test('album page loads within 3 seconds', async ({ page }) => {
    const r = await page.request.post('/api/albums', {
      data: { name: 'Perf Album Page', date: '2026-06-15' },
    });
    const { album } = await r.json();

    const start = Date.now();
    await page.goto(`/albums/${album.id}`);
    await page.waitForLoadState('networkidle');
    const elapsed = Date.now() - start;

    expect(elapsed).toBeLessThan(3000);

    await page.request.delete(`/api/albums/${album.id}`);
  });

  test('album list API responds within 500ms', async ({ page }) => {
    const start = Date.now();
    const res = await page.request.get('/api/albums');
    const elapsed = Date.now() - start;

    expect(res.ok()).toBeTruthy();
    expect(elapsed).toBeLessThan(500);
  });

  test('thumbnail API responds within 500ms for existing photo', async ({ page }) => {
    const r = await page.request.post('/api/albums', {
      data: { name: 'Perf Thumb Album', date: '2026-06-15' },
    });
    const { album } = await r.json();

    // Upload a tiny image via multipart
    const jpgBytes = Buffer.from(
      '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAARC' +
        'AABAAEDASIA2gABAREA/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAAAAAAAAAAAAAAAAAAAAD/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8AJQAB/9k=',
      'base64',
    );

    const uploadRes = await page.request.fetch(`/api/albums/${album.id}/photos`, {
      method: 'POST',
      multipart: { file: { name: 'tiny.jpg', mimeType: 'image/jpeg', buffer: jpgBytes } },
    });

    if (uploadRes.ok()) {
      const { photo } = await uploadRes.json();
      const start = Date.now();
      const thumbRes = await page.request.get(`/api/photos/${photo.id}/thumbnail`);
      const elapsed = Date.now() - start;
      expect(thumbRes.ok()).toBeTruthy();
      expect(elapsed).toBeLessThan(500);
    }

    await page.request.delete(`/api/albums/${album.id}`);
  });
});
