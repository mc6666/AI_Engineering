import { listItems, listWarehouses } from '@/lib/inventory';
import { issueInventoryAction } from '@/app/actions/inventory';

export default async function NewIssuePage({ searchParams }) {
  const { error } = await searchParams;
  const items = listItems({ activeOnly: true });
  const warehouses = listWarehouses({ activeOnly: true });

  return (
    <div className="py-4" style={{ maxWidth: 560 }}>
      <h2>新增出庫</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form action={issueInventoryAction}>
        <div className="mb-3">
          <label className="form-label">商品</label>
          <select name="itemId" className="form-select" required>
            {items.map((it) => (
              <option key={it.id} value={it.id}>
                {it.item_code} - {it.item_name}
              </option>
            ))}
          </select>
        </div>
        <div className="mb-3">
          <label className="form-label">出貨倉庫</label>
          <select name="warehouseId" className="form-select" required>
            {warehouses.map((w) => (
              <option key={w.id} value={w.id}>
                {w.warehouse_code} - {w.warehouse_name}
              </option>
            ))}
          </select>
        </div>
        <div className="mb-3">
          <label className="form-label">數量</label>
          <input type="number" step="0.01" name="quantity" className="form-control" required />
        </div>
        <div className="mb-3">
          <label className="form-label">來源單據（選填）</label>
          <input type="text" name="referenceDoc" className="form-control" placeholder="例如銷售單號" />
        </div>
        <div className="mb-3">
          <label className="form-label">備註（選填）</label>
          <input type="text" name="notes" className="form-control" />
        </div>
        <button type="submit" className="btn btn-primary">
          出庫
        </button>
      </form>
    </div>
  );
}
