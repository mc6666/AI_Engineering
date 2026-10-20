import Link from 'next/link';
import { listTransactions } from '@/lib/inventory';

export default async function ReceiptsPage() {
  const receipts = listTransactions({ type: 'receipt' });

  return (
    <div className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>入庫管理</h2>
        <Link href="/portal/inventory/receipts/new" className="btn btn-primary">
          新增入庫
        </Link>
      </div>
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th>交易編號</th>
            <th>日期</th>
            <th>商品</th>
            <th>倉庫</th>
            <th>批號/序號</th>
            <th>數量</th>
            <th>單位成本</th>
            <th>來源單據</th>
          </tr>
        </thead>
        <tbody>
          {receipts.map((t) => (
            <tr key={t.id}>
              <td>{t.txn_no}</td>
              <td>{t.txn_date}</td>
              <td>
                {t.item_code} {t.item_name}
              </td>
              <td>{t.warehouse_name}</td>
              <td>{t.lot_number || t.serial_number || '-'}</td>
              <td>{t.quantity}</td>
              <td>{t.unit_cost.toFixed(2)}</td>
              <td>{t.reference_doc || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
