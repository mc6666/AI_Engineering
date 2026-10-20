import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getPurchaseOrder } from '@/lib/purchase';
import {
  submitPurchaseOrderAction,
  approvePurchaseOrderAction,
  sendPurchaseOrderAction,
  cancelPurchaseOrderAction,
  closePurchaseOrderAction,
} from '@/app/actions/purchase';

export default async function PurchaseOrderDetailPage({ params, searchParams }) {
  const { id } = await params;
  const { error } = await searchParams;
  const po = getPurchaseOrder(Number(id));
  if (!po) notFound();

  return (
    <div className="py-4">
      <h2>採購訂單：{po.po_no}</h2>
      <p>
        供應商：{po.supplier.supplier_name} ｜ 訂單日期：{po.order_date} ｜ 狀態：<strong>{po.status}</strong>
      </p>
      {error && <div className="alert alert-danger">{error}</div>}
      <table className="table table-bordered">
        <thead>
          <tr>
            <th>商品</th>
            <th>數量</th>
            <th>單價</th>
            <th>折扣%</th>
            <th>已收貨</th>
          </tr>
        </thead>
        <tbody>
          {po.lines.map((l) => (
            <tr key={l.id}>
              <td>
                {l.item_code} {l.item_name}
              </td>
              <td>{l.quantity}</td>
              <td>{l.unit_price.toFixed(2)}</td>
              <td>{l.discount}</td>
              <td>{l.received_qty}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <th colSpan={4}>總金額</th>
            <th>{po.total_amount.toFixed(2)}</th>
          </tr>
        </tfoot>
      </table>

      <div className="d-flex gap-2 flex-wrap">
        {po.status === 'draft' && (
          <form action={submitPurchaseOrderAction}>
            <input type="hidden" name="id" value={po.id} />
            <button type="submit" className="btn btn-primary">
              送出審核
            </button>
          </form>
        )}
        {po.status === 'submitted' && (
          <form action={approvePurchaseOrderAction}>
            <input type="hidden" name="id" value={po.id} />
            <button type="submit" className="btn btn-primary">
              核准
            </button>
          </form>
        )}
        {po.status === 'approved' && (
          <form action={sendPurchaseOrderAction}>
            <input type="hidden" name="id" value={po.id} />
            <button type="submit" className="btn btn-primary">
              發送給供應商
            </button>
          </form>
        )}
        {['sent', 'partially_received'].includes(po.status) && (
          <Link href={`/portal/purchase/receipts/new?poId=${po.id}`} className="btn btn-outline-primary">
            收貨
          </Link>
        )}
        {po.status === 'received' && (
          <Link href={`/portal/purchase/invoices/new?poId=${po.id}`} className="btn btn-outline-primary">
            登錄供應商發票
          </Link>
        )}
        {['draft', 'submitted', 'approved'].includes(po.status) && (
          <form action={cancelPurchaseOrderAction}>
            <input type="hidden" name="id" value={po.id} />
            <button type="submit" className="btn btn-outline-danger">
              取消訂單
            </button>
          </form>
        )}
        {po.status === 'received' && (
          <form action={closePurchaseOrderAction}>
            <input type="hidden" name="id" value={po.id} />
            <button type="submit" className="btn btn-outline-secondary">
              結案
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
