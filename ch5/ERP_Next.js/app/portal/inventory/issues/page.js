import Link from 'next/link';
import { listTransactions } from '@/lib/inventory';

export default async function IssuesPage() {
  const issues = listTransactions({ type: 'issue' });

  return (
    <div className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>出庫管理</h2>
        <Link href="/portal/inventory/issues/new" className="btn btn-primary">
          新增出庫
        </Link>
      </div>
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th>交易編號</th>
            <th>日期</th>
            <th>商品</th>
            <th>倉庫</th>
            <th>數量</th>
            <th>來源單據</th>
          </tr>
        </thead>
        <tbody>
          {issues.map((t) => (
            <tr key={t.id}>
              <td>{t.txn_no}</td>
              <td>{t.txn_date}</td>
              <td>
                {t.item_code} {t.item_name}
              </td>
              <td>{t.warehouse_name}</td>
              <td>{t.quantity}</td>
              <td>{t.reference_doc || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
