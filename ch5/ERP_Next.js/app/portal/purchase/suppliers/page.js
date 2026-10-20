import Link from 'next/link';
import { listSuppliers } from '@/lib/purchase';

export default async function SuppliersPage() {
  const suppliers = listSuppliers();

  return (
    <div className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>供應商管理</h2>
        <Link href="/portal/purchase/suppliers/new" className="btn btn-primary">
          新增供應商
        </Link>
      </div>
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th>供應商代號</th>
            <th>名稱</th>
            <th>付款條件</th>
            <th>信用額度</th>
            <th>評等</th>
            <th>狀態</th>
          </tr>
        </thead>
        <tbody>
          {suppliers.map((s) => (
            <tr key={s.id}>
              <td>
                <Link href={`/portal/purchase/suppliers/${s.id}`}>{s.supplier_code}</Link>
              </td>
              <td>{s.supplier_name}</td>
              <td>{s.payment_terms || '-'}</td>
              <td>{s.credit_limit}</td>
              <td>{s.rating}</td>
              <td>{s.is_active ? '啟用' : '停用'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
