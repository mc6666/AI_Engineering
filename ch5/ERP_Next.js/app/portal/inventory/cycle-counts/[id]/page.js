import { notFound } from 'next/navigation';
import { getCycleCount } from '@/lib/inventory';
import { approveCycleCountAction } from '@/app/actions/inventory';

export default async function CycleCountDetailPage({ params }) {
  const { id } = await params;
  const count = getCycleCount(Number(id));
  if (!count) notFound();

  return (
    <div className="py-4">
      <h2>盤點單：{count.count_no}</h2>
      <p>
        倉庫 ID：{count.warehouse_id} ｜ 狀態：{count.status} ｜ 方式：{count.method}
      </p>
      <table className="table table-bordered">
        <thead>
          <tr>
            <th>商品</th>
            <th>系統數量</th>
            <th>實盤數量</th>
            <th>盤差</th>
          </tr>
        </thead>
        <tbody>
          {count.lines.map((l) => (
            <tr key={l.id} className={l.variance ? 'table-warning' : ''}>
              <td>
                {l.item_code} {l.item_name}
              </td>
              <td>{l.system_qty}</td>
              <td>{l.counted_qty}</td>
              <td>{l.variance}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {count.status === 'open' && (
        <form action={approveCycleCountAction}>
          <input type="hidden" name="id" value={count.id} />
          <button type="submit" className="btn btn-primary">
            核准並更新庫存
          </button>
        </form>
      )}
    </div>
  );
}
