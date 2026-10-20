import { getInventoryDashboard } from '@/lib/inventory';

export default async function InventoryDashboardPage() {
  const d = getInventoryDashboard();

  return (
    <div className="py-4">
      <h2>庫存儀表板</h2>
      <div className="row mt-3">
        <div className="col-md-3">
          <div className="card text-bg-primary mb-3">
            <div className="card-body">
              <div className="fs-4">{d.totalValue.toFixed(2)}</div>
              <div>總庫存價值</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-bg-warning mb-3">
            <div className="card-body">
              <div className="fs-4">{d.lowStockCount}</div>
              <div>低庫存商品</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-bg-secondary mb-3">
            <div className="card-body">
              <div className="fs-4">{d.itemCount}</div>
              <div>啟用商品數</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-bg-secondary mb-3">
            <div className="card-body">
              <div className="fs-4">{d.warehouseCount}</div>
              <div>啟用倉庫數</div>
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-md-6">
          <div className="card mb-3">
            <div className="card-header">低庫存商品（建議補貨）</div>
            <div className="card-body p-0">
              <table className="table table-sm mb-0">
                <thead>
                  <tr>
                    <th>商品</th>
                    <th>可用</th>
                    <th>再訂購點</th>
                    <th>建議採購量</th>
                  </tr>
                </thead>
                <tbody>
                  {d.lowStock.map((s) => (
                    <tr key={s.itemId}>
                      <td>
                        {s.itemCode} {s.itemName}
                      </td>
                      <td>{s.available}</td>
                      <td>{s.reorderPoint}</td>
                      <td>{s.suggestedQty}</td>
                    </tr>
                  ))}
                  {d.lowStock.length === 0 && (
                    <tr>
                      <td colSpan={4}>目前無低庫存商品</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card mb-3">
            <div className="card-header">庫存價值前十大商品</div>
            <div className="card-body p-0">
              <table className="table table-sm mb-0">
                <thead>
                  <tr>
                    <th>商品</th>
                    <th>數量</th>
                    <th>價值</th>
                  </tr>
                </thead>
                <tbody>
                  {d.topItemsByValue.map((l) => (
                    <tr key={l.item_id}>
                      <td>
                        {l.item_code} {l.item_name}
                      </td>
                      <td>{l.qty_on_hand}</td>
                      <td>{l.value.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
