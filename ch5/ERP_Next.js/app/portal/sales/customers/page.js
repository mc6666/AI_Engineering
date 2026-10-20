import Link from 'next/link';
import { listCustomers } from '@/lib/sales';

export default async function CustomersPage() {
  const customers = listCustomers();

  return (
    <div className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>客戶管理</h2>
        <Link href="/portal/sales/customers/new" className="btn btn-primary">
          新增客戶
        </Link>
      </div>
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th>客戶代號</th>
            <th>客戶名稱</th>
            <th>信用額度</th>
            <th>應收餘額</th>
            <th>付款條件</th>
            <th>狀態</th>
          </tr>
        </thead>
        <tbody>
          {customers.map((c) => (
            <tr key={c.id}>
              <td>
                <Link href={`/portal/sales/customers/${c.id}`}>{c.customer_code}</Link>
              </td>
              <td>{c.customer_name}</td>
              <td>{c.credit_limit}</td>
              <td>{c.ar_balance}</td>
              <td>{c.payment_terms || '-'}</td>
              <td>{c.is_active ? '啟用' : '停用'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
