import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getPurchaseRequisition } from '@/lib/purchase';
import { approveRequisitionAction } from '@/app/actions/purchase';

export default async function RequisitionDetailPage({ params }) {
  const { id } = await params;
  const pr = getPurchaseRequisition(Number(id));
  if (!pr) notFound();

  return (
    <div className="py-4">
      <h2>請購單：{pr.pr_no}</h2>
      <p>
        部門：{pr.department || '-'} ｜ 需求日期：{pr.required_date || '-'} ｜ 狀態：{pr.status}
      </p>
      <p>採購原因：{pr.reason || '-'}</p>
      <table className="table table-bordered">
        <thead>
          <tr>
            <th>商品</th>
            <th>數量</th>
          </tr>
        </thead>
        <tbody>
          {pr.lines.map((l) => (
            <tr key={l.id}>
              <td>
                {l.item_code} {l.item_name}
              </td>
              <td>{l.quantity}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="d-flex gap-2">
        {pr.status === 'draft' && (
          <form action={approveRequisitionAction}>
            <input type="hidden" name="id" value={pr.id} />
            <button type="submit" className="btn btn-primary">
              核准請購單
            </button>
          </form>
        )}
        {pr.status === 'approved' && (
          <Link href={`/portal/purchase/rfq/new?prId=${pr.id}`} className="btn btn-outline-primary">
            建立詢價單
          </Link>
        )}
        {pr.status === 'approved' && (
          <Link href={`/portal/purchase/orders/new?prId=${pr.id}`} className="btn btn-outline-primary">
            建立採購訂單
          </Link>
        )}
      </div>
    </div>
  );
}
