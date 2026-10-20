import Link from 'next/link';
import { listRFQs } from '@/lib/purchase';

export default async function RFQsPage() {
  const rfqs = listRFQs();

  return (
    <div className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>詢價比價</h2>
        <Link href="/portal/purchase/rfq/new" className="btn btn-primary">
          新增詢價單
        </Link>
      </div>
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th>詢價單號</th>
            <th>報價截止日</th>
            <th>狀態</th>
          </tr>
        </thead>
        <tbody>
          {rfqs.map((r) => (
            <tr key={r.id}>
              <td>
                <Link href={`/portal/purchase/rfq/${r.id}`}>{r.rfq_no}</Link>
              </td>
              <td>{r.quote_due_date || '-'}</td>
              <td>{r.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
