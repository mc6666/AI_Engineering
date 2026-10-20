import { listItems, listWarehouses } from '@/lib/inventory';
import { transferInventoryAction } from '@/app/actions/inventory';

export default async function NewTransferPage({ searchParams }) {
  const { error } = await searchParams;
  const items = listItems({ activeOnly: true });
  const warehouses = listWarehouses({ activeOnly: true });

  return (
    <div className="py-4" style={{ maxWidth: 560 }}>
      <h2>新增庫存調撥</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form action={transferInventoryAction}>
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
        <div className="row">
          <div className="col-md-6 mb-3">
            <label className="form-label">調出倉庫</label>
            <select name="fromWarehouseId" className="form-select" required>
              {warehouses.map((w) => (
                <option key={w.id} value={w.id}>
                  {w.warehouse_code} - {w.warehouse_name}
                </option>
              ))}
            </select>
          </div>
          <div className="col-md-6 mb-3">
            <label className="form-label">調入倉庫</label>
            <select name="toWarehouseId" className="form-select" required>
              {warehouses.map((w) => (
                <option key={w.id} value={w.id}>
                  {w.warehouse_code} - {w.warehouse_name}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="mb-3">
          <label className="form-label">數量</label>
          <input type="number" step="0.01" name="quantity" className="form-control" required />
        </div>
        <div className="mb-3">
          <label className="form-label">備註（選填）</label>
          <input type="text" name="referenceDoc" className="form-control" />
        </div>
        <button type="submit" className="btn btn-primary">
          調撥
        </button>
      </form>
    </div>
  );
}
