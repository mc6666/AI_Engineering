import { listWarehouses, searchInventory } from '@/lib/inventory';
import { performPhysicalCountAction } from '@/app/actions/inventory';

export default async function NewPhysicalCountPage({ searchParams }) {
  const { error, warehouseId } = await searchParams;
  const warehouses = listWarehouses({ activeOnly: true });
  const selectedWarehouseId = warehouseId ? Number(warehouseId) : null;
  const stock = selectedWarehouseId ? searchInventory({ warehouseId: selectedWarehouseId }) : [];

  return (
    <div className="py-4" style={{ maxWidth: 720 }}>
      <h2>新增全面盤點</h2>
      <p className="text-muted">全面盤點會凍結整個倉庫的庫存交易，請於盤點完成後核准。</p>
      {error && <div className="alert alert-danger">{error}</div>}

      <form method="get" className="row g-2 align-items-end mb-4">
        <div className="col-md-8">
          <label className="form-label">倉庫</label>
          <select name="warehouseId" className="form-select" defaultValue={selectedWarehouseId || ''}>
            <option value="" disabled>
              請選擇倉庫
            </option>
            {warehouses.map((w) => (
              <option key={w.id} value={w.id}>
                {w.warehouse_code} - {w.warehouse_name}
              </option>
            ))}
          </select>
        </div>
        <div className="col-md-4">
          <button type="submit" className="btn btn-secondary">
            載入庫存
          </button>
        </div>
      </form>

      {selectedWarehouseId && stock.length > 0 && (
        <form action={performPhysicalCountAction}>
          <input type="hidden" name="warehouseId" value={selectedWarehouseId} />
          <table className="table table-bordered">
            <thead>
              <tr>
                <th>商品</th>
                <th>批號/序號</th>
                <th>系統數量</th>
                <th>實盤數量</th>
              </tr>
            </thead>
            <tbody>
              {stock.map((s) => (
                <tr key={s.id}>
                  <td>
                    {s.item_code} {s.item_name}
                    <input type="hidden" name="stockId" value={s.id} />
                  </td>
                  <td>{s.lot_number || s.serial_number || '-'}</td>
                  <td>{s.qty_on_hand}</td>
                  <td>
                    <input
                      type="number"
                      step="0.01"
                      name="countedQty"
                      className="form-control"
                      defaultValue={s.qty_on_hand}
                      required
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <button type="submit" className="btn btn-primary">
            凍結並送出盤點
          </button>
        </form>
      )}
      {selectedWarehouseId && stock.length === 0 && <p>此倉庫尚無庫存紀錄。</p>}
    </div>
  );
}
