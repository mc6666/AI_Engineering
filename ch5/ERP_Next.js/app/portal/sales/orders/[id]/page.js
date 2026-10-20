import { notFound } from 'next/navigation';
import { getSalesOrder } from '@/lib/sales';
import {
  submitOrderAction,
  approveOrderAction,
  cancelOrderAction,
  closeOrderAction,
  duplicateOrderAction,
  createShipmentAction,
  createInvoiceAction,
} from '@/app/actions/sales';

export default async function SalesOrderDetailPage({ params, searchParams }) {
  const { id } = await params;
  const { error } = await searchParams;
  const so = getSalesOrder(Number(id));
  if (!so) notFound();

  return (
    <div className="py-4">
      <h2>銷售訂單：{so.so_no}</h2>
      <p>
        客戶：{so.customer.customer_name} ｜ 訂單日期：{so.order_date} ｜ 狀態：<strong>{so.status}</strong>
      </p>
      {error && <div className="alert alert-danger">{error}</div>}
      <table className="table table-bordered">
        <thead>
          <tr>
            <th>商品</th>
            <th>數量</th>
            <th>單價</th>
            <th>折扣%</th>
            <th>已出貨</th>
          </tr>
        </thead>
        <tbody>
          {so.lines.map((l) => (
            <tr key={l.id}>
              <td>
                {l.item_code} {l.item_name}
              </td>
              <td>{l.quantity}</td>
              <td>{l.unit_price.toFixed(2)}</td>
              <td>{l.discount}</td>
              <td>{l.shipped_qty}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <th colSpan={4}>總金額</th>
            <th>{so.total_amount.toFixed(2)}</th>
          </tr>
        </tfoot>
      </table>

      <div className="d-flex gap-2 flex-wrap">
        {so.status === 'draft' && (
          <form action={submitOrderAction}>
            <input type="hidden" name="id" value={so.id} />
            <button type="submit" className="btn btn-primary">
              送出訂單
            </button>
          </form>
        )}
        {so.status === 'open' && (
          <form action={approveOrderAction}>
            <input type="hidden" name="id" value={so.id} />
            <button type="submit" className="btn btn-primary">
              核准並預留庫存
            </button>
          </form>
        )}
        {so.status === 'approved' && (
          <form action={createShipmentAction} className="d-flex gap-2 align-items-end">
            <input type="hidden" name="soId" value={so.id} />
            <div>
              <label className="form-label small mb-0">物流追蹤號碼</label>
              <input type="text" name="trackingNo" className="form-control form-control-sm" />
            </div>
            <div>
              <label className="form-label small mb-0">承運商</label>
              <input type="text" name="carrier" className="form-control form-control-sm" />
            </div>
            <div>
              <label className="form-label small mb-0">出貨日期</label>
              <input type="date" name="shipDate" className="form-control form-control-sm" />
            </div>
            <button type="submit" className="btn btn-primary btn-sm">
              出貨
            </button>
          </form>
        )}
        {so.status === 'shipped' && (
          <form action={createInvoiceAction}>
            <input type="hidden" name="soId" value={so.id} />
            <button type="submit" className="btn btn-outline-primary">
              開立發票
            </button>
          </form>
        )}
        {['draft', 'open', 'approved'].includes(so.status) && (
          <form action={cancelOrderAction}>
            <input type="hidden" name="id" value={so.id} />
            <button type="submit" className="btn btn-outline-danger">
              取消訂單
            </button>
          </form>
        )}
        {so.status === 'invoiced' && (
          <form action={closeOrderAction}>
            <input type="hidden" name="id" value={so.id} />
            <button type="submit" className="btn btn-outline-secondary">
              結案
            </button>
          </form>
        )}
        <form action={duplicateOrderAction}>
          <input type="hidden" name="id" value={so.id} />
          <button type="submit" className="btn btn-outline-secondary">
            複製訂單
          </button>
        </form>
      </div>
    </div>
  );
}
