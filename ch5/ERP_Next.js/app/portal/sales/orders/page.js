import Link from 'next/link';
import { listSalesOrders } from '@/lib/sales';

export default async function SalesOrdersPage({ searchParams }) {
  const { message } = await searchParams;
  const orders = listSalesOrders();

  return (
    <div className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>銷售訂單</h2>
        <div className="d-flex gap-2">
          <Link href="/portal/sales/orders/import" className="btn btn-outline-secondary">
            匯入
          </Link>
          <a href="/portal/sales/orders/export" className="btn btn-outline-secondary">
            匯出CSV
          </a>
          <Link href="/portal/sales/orders/new" className="btn btn-primary">
            新增銷售訂單
          </Link>
        </div>
      </div>
      {message && <div className="alert alert-info">{message}</div>}
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th>訂單編號</th>
            <th>客戶</th>
            <th>訂單日期</th>
            <th>總金額</th>
            <th>狀態</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((so) => (
            <tr key={so.id}>
              <td>
                <Link href={`/portal/sales/orders/${so.id}`}>{so.so_no}</Link>
              </td>
              <td>{so.customer_name}</td>
              <td>{so.order_date}</td>
              <td>{so.total_amount.toFixed(2)}</td>
              <td>{so.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
