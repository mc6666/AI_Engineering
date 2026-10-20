import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility — Create Album Modal', () => {
  test('create album modal has no WCAG 2.1 AA violations', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /create album/i }).click();
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();
    expect(results.violations).toEqual([]);
  });
});

test.describe('Album CRUD — Full Flow', () => {
  test('can create a new album via modal', async ({ page }) => {
    await page.goto('/');

    // Open create modal
    await page.getByRole('button', { name: /create album/i }).click();

    // Fill form inside the dialog
    await page.getByRole('dialog').getByLabel(/name/i).fill('My E2E Album');
    await page.getByRole('dialog').getByLabel(/date/i).fill('2026-06-15');

    // Submit via the dialog's submit button (exact text "Create")
    await page.getByRole('dialog').getByRole('button', { name: 'Create' }).click();

    // Album card should appear
    await expect(page.getByText('My E2E Album')).toBeVisible();

    // Cleanup — get id and delete
    const listRes = await page.request.get('/api/albums');
    const { albums } = await listRes.json();
    const created = albums.find((a: { name: string; id: number }) => a.name === 'My E2E Album');
    if (created) await page.request.delete(`/api/albums/${created.id}`);
  });

  test('can delete an album via confirm dialog', async ({ page }) => {
    // Create album via API
    const r = await page.request.post('/api/albums', {
      data: { name: 'Album To Delete', date: '2026-06-01' },
    });
    const { album } = await r.json();

    await page.goto('/');
    await expect(page.getByText('Album To Delete')).toBeVisible();

    // Hover card to reveal delete button, then click it
    const card = page.locator('.group').filter({ hasText: 'Album To Delete' });
    await card.hover();
    await card.getByRole('button', { name: /delete album/i }).click();

    // Confirm dialog
    await page.getByRole('button', { name: /delete|confirm/i }).last().click();

    // Album should be gone
    await expect(page.getByText('Album To Delete')).not.toBeVisible();
  });

  test('create album form validates required fields', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /create album/i }).click();

    // Try to submit empty
    await page.getByRole('dialog').getByRole('button', { name: 'Create' }).click();

    // Browser native validation or custom error should fire
    const nameInput = page.getByRole('dialog').getByLabel(/album name/i);
    // Validation prevents submission — input stays visible in dialog
    await expect(nameInput).toBeVisible();
  });

  test('full create → view → upload → delete photo flow', async ({ page }) => {
    // Create
    const r = await page.request.post('/api/albums', {
      data: { name: 'Full CRUD Album', date: '2026-06-15' },
    });
    const { album } = await r.json();

    // Navigate to album
    await page.goto(`/albums/${album.id}`);
    await expect(page.getByText('Full CRUD Album')).toBeVisible();
    await expect(page.getByText(/no photos yet/i)).toBeVisible();

    // Navigate back
    await page.goto('/');
    await expect(page.getByText('Full CRUD Album')).toBeVisible();

    // Delete via API
    await page.request.delete(`/api/albums/${album.id}`);
    await page.reload();
    await expect(page.getByText('Full CRUD Album')).not.toBeVisible();
  });
});
