import Link from 'next/link';
import { listGoodsReceipts } from '@/lib/purchase';

export default async function GoodsReceiptsPage() {
  const receipts = listGoodsReceipts();

  return (
    <div className="py-4">
      <h2>收貨管理</h2>
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th>收貨單號</th>
            <th>採購單號</th>
            <th>收貨日期</th>
            <th>狀態</th>
          </tr>
        </thead>
        <tbody>
          {receipts.map((g) => (
            <tr key={g.id}>
              <td>
                <Link href={`/portal/purchase/receipts/${g.id}`}>{g.grn_no}</Link>
              </td>
              <td>{g.po_no}</td>
              <td>{g.received_date}</td>
              <td>{g.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="text-muted">請由採購訂單詳細頁面點選「收貨」以建立新的收貨單。</p>
    </div>
  );
}
