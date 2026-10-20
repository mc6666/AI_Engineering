import Link from 'next/link';
import { listPurchaseRequisitions } from '@/lib/purchase';

export default async function RequisitionsPage() {
  const prs = listPurchaseRequisitions();

  return (
    <div className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>請購單</h2>
        <Link href="/portal/purchase/requisitions/new" className="btn btn-primary">
          新增請購單
        </Link>
      </div>
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th>請購單號</th>
            <th>申請人</th>
            <th>部門</th>
            <th>需求日期</th>
            <th>狀態</th>
          </tr>
        </thead>
        <tbody>
          {prs.map((pr) => (
            <tr key={pr.id}>
              <td>
                <Link href={`/portal/purchase/requisitions/${pr.id}`}>{pr.pr_no}</Link>
              </td>
              <td>{pr.requester_name}</td>
              <td>{pr.department || '-'}</td>
              <td>{pr.required_date || '-'}</td>
              <td>{pr.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
