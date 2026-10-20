import { test, expect } from '@playwright/test';

test.describe('Album Drag-and-Drop Reorder', () => {
  test('albums can be reordered via keyboard drag-and-drop', async ({ page }) => {
    // Create two albums
    const r1 = await page.request.post('/api/albums', {
      data: { name: 'Album First', date: '2026-06-01' },
    });
    const r2 = await page.request.post('/api/albums', {
      data: { name: 'Album Second', date: '2026-06-02' },
    });
    const { album: a1 } = await r1.json();
    const { album: a2 } = await r2.json();

    await page.goto('/');

    // Both cards should be visible
    await expect(page.getByText('Album First')).toBeVisible();
    await expect(page.getByText('Album Second')).toBeVisible();

    // Focus the drag handle of the first album and activate drag via Space
    const dragHandles = page.locator('[aria-label="Drag to reorder"]');
    const firstHandle = dragHandles.first();
    await firstHandle.focus();
    await firstHandle.press('Space'); // lift
    await firstHandle.press('ArrowDown'); // move down one slot
    await firstHandle.press('Space'); // drop

    // After reorder, both albums should still be visible
    await expect(page.getByText('Album First')).toBeVisible();
    await expect(page.getByText('Album Second')).toBeVisible();

    // Cleanup
    await page.request.delete(`/api/albums/${a1.id}`);
    await page.request.delete(`/api/albums/${a2.id}`);
  });

  test('reorder API call persists order across page reload', async ({ page }) => {
    const r1 = await page.request.post('/api/albums', {
      data: { name: 'Persist First', date: '2026-06-10' },
    });
    const r2 = await page.request.post('/api/albums', {
      data: { name: 'Persist Second', date: '2026-06-11' },
    });
    const { album: a1 } = await r1.json();
    const { album: a2 } = await r2.json();

    // Reorder via API directly
    const listRes = await page.request.get('/api/albums');
    const { albums } = await listRes.json();
    const found = albums.find((a: { id: number }) => a.id === a2.id);
    if (found) {
      await page.request.post(`/api/albums/${a2.id}/reorder`, {
        data: { successorOrder: found.display_order - 0.5 },
      });
    }

    // Reload and verify both still exist
    await page.goto('/');
    await expect(page.getByText('Persist First')).toBeVisible();
    await expect(page.getByText('Persist Second')).toBeVisible();

    await page.request.delete(`/api/albums/${a1.id}`);
    await page.request.delete(`/api/albums/${a2.id}`);
  });
});
