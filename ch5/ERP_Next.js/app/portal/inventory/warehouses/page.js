import Link from 'next/link';
import { listWarehouses } from '@/lib/inventory';

export default async function WarehousesPage() {
  const warehouses = listWarehouses();

  return (
    <div className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>倉庫管理</h2>
        <Link href="/portal/inventory/warehouses/new" className="btn btn-primary">
          新增倉庫
        </Link>
      </div>
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th>倉庫代號</th>
            <th>倉庫名稱</th>
            <th>位置</th>
            <th>狀態</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {warehouses.map((w) => (
            <tr key={w.id}>
              <td>{w.warehouse_code}</td>
              <td>{w.warehouse_name}</td>
              <td>{w.location || '-'}</td>
              <td>{w.is_active ? '啟用' : '停用'}</td>
              <td>
                <Link href={`/portal/inventory/warehouses/${w.id}`} className="btn btn-sm btn-secondary">
                  編輯
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
