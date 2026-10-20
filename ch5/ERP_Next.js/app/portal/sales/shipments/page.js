import Link from 'next/link';
import { listShipments } from '@/lib/sales';

export default async function ShipmentsPage() {
  const shipments = listShipments();

  return (
    <div className="py-4">
      <h2>出貨管理</h2>
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th>出貨單號</th>
            <th>銷售訂單</th>
            <th>客戶</th>
            <th>承運商</th>
            <th>物流追蹤號碼</th>
            <th>出貨日期</th>
          </tr>
        </thead>
        <tbody>
          {shipments.map((sh) => (
            <tr key={sh.id}>
              <td>{sh.shipment_no}</td>
              <td>
                <Link href={`/portal/sales/orders/${sh.so_id}`}>{sh.so_no}</Link>
              </td>
              <td>{sh.customer_name}</td>
              <td>{sh.carrier || '-'}</td>
              <td>{sh.tracking_no || '-'}</td>
              <td>{sh.ship_date || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="text-muted">請由銷售訂單詳細頁面出貨。</p>
    </div>
  );
}
