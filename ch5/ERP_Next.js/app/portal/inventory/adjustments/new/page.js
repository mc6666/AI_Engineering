import { listItems, listWarehouses } from '@/lib/inventory';
import { adjustInventoryAction } from '@/app/actions/inventory';

export default async function NewAdjustmentPage({ searchParams }) {
  const { error } = await searchParams;
  const items = listItems({ activeOnly: true });
  const warehouses = listWarehouses({ activeOnly: true });

  return (
    <div className="py-4" style={{ maxWidth: 560 }}>
      <h2>新增庫存調整</h2>
      <p className="text-muted">調整需填寫原因；送出者即視為核准者。</p>
      {error && <div className="alert alert-danger">{error}</div>}
      <form action={adjustInventoryAction}>
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
          <label className="form-label">倉庫</label>
          <select name="warehouseId" className="form-select" required>
            {warehouses.map((w) => (
              <option key={w.id} value={w.id}>
                {w.warehouse_code} - {w.warehouse_name}
              </option>
            ))}
          </select>
        </div>
        <div className="mb-3">
          <label className="form-label">調整數量（正數增加、負數減少）</label>
          <input type="number" step="0.01" name="quantityDelta" className="form-control" required />
        </div>
        <div className="mb-3">
          <label className="form-label">原因</label>
          <input type="text" name="reason" className="form-control" required />
        </div>
        <button type="submit" className="btn btn-primary">
          送出
        </button>
      </form>
    </div>
  );
}
