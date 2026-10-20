import Link from 'next/link';
import { listPhysicalInventories } from '@/lib/inventory';

export default async function PhysicalCountsPage() {
  const counts = listPhysicalInventories();

  return (
    <div className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>全面盤點</h2>
        <Link href="/portal/inventory/physical-counts/new" className="btn btn-primary">
          新增全面盤點
        </Link>
      </div>
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th>盤點單號</th>
            <th>倉庫</th>
            <th>狀態</th>
            <th>建立時間</th>
          </tr>
        </thead>
        <tbody>
          {counts.map((c) => (
            <tr key={c.id}>
              <td>
                <Link href={`/portal/inventory/physical-counts/${c.id}`}>{c.count_no}</Link>
              </td>
              <td>{c.warehouse_name}</td>
              <td>{c.status}</td>
              <td>{c.created_at}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
