import { generateInventoryReport } from '@/lib/inventory';

const REPORT_TYPES = [
  { value: 'valuation', label: '庫存價值報表' },
  { value: 'low_stock', label: '補貨建議報表' },
  { value: 'status', label: '庫存狀況報表' },
  { value: 'turnover', label: '庫存週轉率報表' },
];

export default async function InventoryReportsPage({ searchParams }) {
  const { type = 'valuation' } = await searchParams;
  const report = generateInventoryReport({ type });

  return (
    <div className="py-4">
      <h2>庫存報表</h2>
      <form method="get" className="d-flex gap-2 mb-3" style={{ maxWidth: 420 }}>
        <select name="type" className="form-select" defaultValue={type}>
          {REPORT_TYPES.map((r) => (
            <option key={r.value} value={r.value}>
              {r.label}
            </option>
          ))}
        </select>
        <button type="submit" className="btn btn-secondary text-nowrap">
          查詢
        </button>
      </form>

      {type === 'valuation' && (
        <table className="table table-striped table-bordered">
          <thead>
            <tr>
              <th>商品</th>
              <th>數量</th>
              <th>價值</th>
            </tr>
          </thead>
          <tbody>
            {report.lines.map((l) => (
              <tr key={l.item_id}>
                <td>
                  {l.item_code} {l.item_name}
                </td>
                <td>{l.qty_on_hand}</td>
                <td>{l.value.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr>
              <th colSpan={2}>合計</th>
              <th>{report.totalValue.toFixed(2)}</th>
            </tr>
          </tfoot>
        </table>
      )}

      {type === 'low_stock' && (
        <table className="table table-striped table-bordered">
          <thead>
            <tr>
              <th>商品</th>
              <th>可用庫存</th>
              <th>再訂購點</th>
              <th>建議採購量</th>
            </tr>
          </thead>
          <tbody>
            {report.map((s) => (
              <tr key={s.itemId}>
                <td>
                  {s.itemCode} {s.itemName}
                </td>
                <td>{s.available}</td>
                <td>{s.reorderPoint}</td>
                <td>{s.suggestedQty}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {type === 'status' && (
        <table className="table table-striped table-bordered">
          <thead>
            <tr>
              <th>狀態</th>
              <th>庫存筆數</th>
              <th>數量</th>
            </tr>
          </thead>
          <tbody>
            {report.map((r) => (
              <tr key={r.status}>
                <td>{r.status}</td>
                <td>{r.lines}</td>
                <td>{r.qty}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {type === 'turnover' && (
        <table className="table table-striped table-bordered">
          <thead>
            <tr>
              <th>商品</th>
              <th>累計出庫量</th>
              <th>目前庫存量</th>
            </tr>
          </thead>
          <tbody>
            {report.map((r) => (
              <tr key={r.item_code}>
                <td>
                  {r.item_code} {r.item_name}
                </td>
                <td>{r.issued_qty}</td>
                <td>{r.on_hand_qty}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
