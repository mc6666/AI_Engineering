import { listItems, listWarehouses } from '@/lib/inventory';
import { receiveInventoryAction } from '@/app/actions/inventory';

export default async function NewReceiptPage({ searchParams }) {
  const { error } = await searchParams;
  const items = listItems({ activeOnly: true });
  const warehouses = listWarehouses({ activeOnly: true });

  return (
    <div className="py-4" style={{ maxWidth: 560 }}>
      <h2>新增入庫</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form action={receiveInventoryAction}>
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
          <label className="form-label">收貨倉庫</label>
          <select name="warehouseId" className="form-select" required>
            {warehouses.map((w) => (
              <option key={w.id} value={w.id}>
                {w.warehouse_code} - {w.warehouse_name}
              </option>
            ))}
          </select>
        </div>
        <div className="row">
          <div className="col-md-6 mb-3">
            <label className="form-label">數量</label>
            <input type="number" step="0.01" name="quantity" className="form-control" required />
          </div>
          <div className="col-md-6 mb-3">
            <label className="form-label">單位成本</label>
            <input type="number" step="0.01" name="unitCost" className="form-control" defaultValue="0" />
          </div>
        </div>
        <div className="row">
          <div className="col-md-6 mb-3">
            <label className="form-label">批號（選填）</label>
            <input type="text" name="lotNumber" className="form-control" />
          </div>
          <div className="col-md-6 mb-3">
            <label className="form-label">序號（選填）</label>
            <input type="text" name="serialNumber" className="form-control" />
          </div>
        </div>
        <div className="row">
          <div className="col-md-6 mb-3">
            <label className="form-label">效期（選填）</label>
            <input type="date" name="expirationDate" className="form-control" />
          </div>
          <div className="col-md-6 mb-3">
            <label className="form-label">來源單據（選填）</label>
            <input type="text" name="referenceDoc" className="form-control" placeholder="例如採購單號" />
          </div>
        </div>
        <button type="submit" className="btn btn-primary">
          入庫
        </button>
      </form>
    </div>
  );
}
