import Link from 'next/link';
import { listPurchaseOrders } from '@/lib/purchase';

export default async function PurchaseOrdersPage() {
  const orders = listPurchaseOrders();

  return (
    <div className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>採購訂單</h2>
        <Link href="/portal/purchase/orders/new" className="btn btn-primary">
          新增採購訂單
        </Link>
      </div>
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th>採購單號</th>
            <th>供應商</th>
            <th>訂單日期</th>
            <th>總金額</th>
            <th>狀態</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((po) => (
            <tr key={po.id}>
              <td>
                <Link href={`/portal/purchase/orders/${po.id}`}>{po.po_no}</Link>
              </td>
              <td>{po.supplier_name}</td>
              <td>{po.order_date}</td>
              <td>{po.total_amount.toFixed(2)}</td>
              <td>{po.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
