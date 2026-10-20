import { generateReorderSuggestion } from '@/lib/inventory';

export default async function ReorderPage() {
  const suggestions = generateReorderSuggestion();

  return (
    <div className="py-4">
      <h2>補貨建議</h2>
      <p className="text-muted">
        依可用庫存、再訂購點與安全庫存計算：建議採購量 = 再訂購點 + 安全庫存 − 可用庫存。
      </p>
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th>商品</th>
            <th>可用庫存</th>
            <th>再訂購點</th>
            <th>安全庫存</th>
            <th>前置時間（天）</th>
            <th>建議採購量</th>
          </tr>
        </thead>
        <tbody>
          {suggestions.map((s) => (
            <tr key={s.itemId}>
              <td>
                {s.itemCode} {s.itemName}
              </td>
              <td>{s.available}</td>
              <td>{s.reorderPoint}</td>
              <td>{s.safetyStock}</td>
              <td>{s.leadTimeDays}</td>
              <td className="fw-bold">{s.suggestedQty}</td>
            </tr>
          ))}
          {suggestions.length === 0 && (
            <tr>
              <td colSpan={6}>目前無補貨建議</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
