import Link from 'next/link';
import { listTransactions } from '@/lib/inventory';

export default async function AdjustmentsPage() {
  const adjustments = listTransactions({ type: 'adjustment' });

  return (
    <div className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>庫存調整</h2>
        <Link href="/portal/inventory/adjustments/new" className="btn btn-primary">
          新增調整
        </Link>
      </div>
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th>交易編號</th>
            <th>日期</th>
            <th>商品</th>
            <th>倉庫</th>
            <th>調整數量</th>
            <th>原因</th>
          </tr>
        </thead>
        <tbody>
          {adjustments.map((t) => (
            <tr key={t.id}>
              <td>{t.txn_no}</td>
              <td>{t.txn_date}</td>
              <td>
                {t.item_code} {t.item_name}
              </td>
              <td>{t.warehouse_name}</td>
              <td>{t.quantity}</td>
              <td>{t.notes || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
