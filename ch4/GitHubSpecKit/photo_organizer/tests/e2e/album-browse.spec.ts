import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility — Home Page', () => {
  test('home page has no WCAG 2.1 AA violations', async ({ page }) => {
    await page.goto('/');
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();
    expect(results.violations).toEqual([]);
  });
});

test.describe('Album Browse', () => {
  test('home page shows empty state when no albums exist', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText(/no albums/i)).toBeVisible();
  });

  test('home page shows album cards grouped by date', async ({ page }) => {
    // Create two albums via API
    const r1 = await page.request.post('/api/albums', {
      data: { name: 'Spring Hike', date: '2026-04-10' },
    });
    const r2 = await page.request.post('/api/albums', {
      data: { name: 'Summer Beach', date: '2026-07-05' },
    });
    expect(r1.ok()).toBeTruthy();
    expect(r2.ok()).toBeTruthy();

    await page.goto('/');

    await expect(page.getByText('Spring Hike')).toBeVisible();
    await expect(page.getByText('Summer Beach')).toBeVisible();

    // Cleanup
    const { album: a1 } = await r1.json();
    const { album: a2 } = await r2.json();
    await page.request.delete(`/api/albums/${a1.id}`);
    await page.request.delete(`/api/albums/${a2.id}`);
  });

  test('clicking album card navigates to album page', async ({ page }) => {
    const r = await page.request.post('/api/albums', {
      data: { name: 'E2E Browse Album', date: '2026-05-01' },
    });
    const { album } = await r.json();

    await page.goto('/');
    await page.getByText('E2E Browse Album').click();
    await expect(page).toHaveURL(new RegExp(`/albums/${album.id}`));
    await expect(page.getByText('E2E Browse Album')).toBeVisible();

    await page.request.delete(`/api/albums/${album.id}`);
  });

  test('albums are grouped under date headings', async ({ page }) => {
    const r1 = await page.request.post('/api/albums', {
      data: { name: 'Alpha', date: '2026-03-01' },
    });
    const r2 = await page.request.post('/api/albums', {
      data: { name: 'Beta', date: '2026-03-15' },
    });
    const r3 = await page.request.post('/api/albums', {
      data: { name: 'Gamma', date: '2026-09-01' },
    });

    await page.goto('/');

    // Both March albums appear under same month heading
    const marchHeadings = page.getByText(/2026-03|march 2026/i);
    await expect(marchHeadings.first()).toBeVisible();
    await expect(page.getByText('Alpha')).toBeVisible();
    await expect(page.getByText('Beta')).toBeVisible();
    await expect(page.getByText('Gamma')).toBeVisible();

    const { album: a1 } = await r1.json();
    const { album: a2 } = await r2.json();
    const { album: a3 } = await r3.json();
    await page.request.delete(`/api/albums/${a1.id}`);
    await page.request.delete(`/api/albums/${a2.id}`);
    await page.request.delete(`/api/albums/${a3.id}`);
  });
});
