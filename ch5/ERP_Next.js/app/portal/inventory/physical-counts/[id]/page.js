import { notFound } from 'next/navigation';
import { getPhysicalInventory } from '@/lib/inventory';
import { completePhysicalCountAction } from '@/app/actions/inventory';

export default async function PhysicalCountDetailPage({ params }) {
  const { id } = await params;
  const pi = getPhysicalInventory(Number(id));
  if (!pi) notFound();

  return (
    <div className="py-4">
      <h2>全面盤點單：{pi.count_no}</h2>
      <p>狀態：{pi.status}</p>
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
          {pi.lines.map((l) => (
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
      {pi.status === 'frozen' && (
        <form action={completePhysicalCountAction}>
          <input type="hidden" name="id" value={pi.id} />
          <button type="submit" className="btn btn-primary">
            核准並更新庫存
          </button>
        </form>
      )}
    </div>
  );
}
