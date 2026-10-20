import Link from 'next/link';
import { listItems } from '@/lib/inventory';

export default async function ItemsPage() {
  const items = listItems();

  return (
    <div className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>商品主檔</h2>
        <Link href="/portal/inventory/items/new" className="btn btn-primary">
          新增商品
        </Link>
      </div>
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th>商品代號</th>
            <th>商品名稱</th>
            <th>分類</th>
            <th>單位</th>
            <th>成本法</th>
            <th>平均成本</th>
            <th>再訂購點</th>
            <th>狀態</th>
          </tr>
        </thead>
        <tbody>
          {items.map((it) => (
            <tr key={it.id}>
              <td>
                <Link href={`/portal/inventory/items/${it.id}`}>{it.item_code}</Link>
              </td>
              <td>{it.item_name}</td>
              <td>{it.category || '-'}</td>
              <td>{it.uom}</td>
              <td>{it.costing_method}</td>
              <td>{it.average_cost.toFixed(2)}</td>
              <td>{it.reorder_point}</td>
              <td>{it.is_active ? '啟用' : '停用'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
