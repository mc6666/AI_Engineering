import Link from 'next/link';
import { listCycleCounts } from '@/lib/inventory';

export default async function CycleCountsPage() {
  const counts = listCycleCounts();

  return (
    <div className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>循環盤點</h2>
        <Link href="/portal/inventory/cycle-counts/new" className="btn btn-primary">
          新增盤點
        </Link>
      </div>
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th>盤點單號</th>
            <th>倉庫</th>
            <th>方式</th>
            <th>狀態</th>
            <th>建立時間</th>
          </tr>
        </thead>
        <tbody>
          {counts.map((c) => (
            <tr key={c.id}>
              <td>
                <Link href={`/portal/inventory/cycle-counts/${c.id}`}>{c.count_no}</Link>
              </td>
              <td>{c.warehouse_name}</td>
              <td>{c.method}</td>
              <td>{c.status}</td>
              <td>{c.created_at}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
