import { notFound } from 'next/navigation';
import { getPurchaseOrder } from '@/lib/purchase';
import { listWarehouses } from '@/lib/inventory';
import { receiveGoodsAction } from '@/app/actions/purchase';

export default async function NewGoodsReceiptPage({ searchParams }) {
  const { error, poId } = await searchParams;
  if (!poId) notFound();
  const po = getPurchaseOrder(Number(poId));
  if (!po) notFound();
  const warehouses = listWarehouses({ activeOnly: true });
  const openLines = po.lines.filter((l) => l.received_qty < l.quantity);

  return (
    <div className="py-4" style={{ maxWidth: 720 }}>
      <h2>收貨：{po.po_no}</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form action={receiveGoodsAction}>
        <input type="hidden" name="poId" value={po.id} />
        <div className="mb-3">
          <label className="form-label">收貨倉庫</label>
          <select name="warehouseId" className="form-select" required>
            {warehouses.map((w) => (
              <option key={w.id} value={w.id}>
                {w.warehouse_code} - {w.warehouse_name}
              </option>
            ))}
          </select>
        </div>
        <table className="table table-bordered">
          <thead>
            <tr>
              <th>商品</th>
              <th>訂購量</th>
              <th>已收貨</th>
              <th>本次收貨數量</th>
            </tr>
          </thead>
          <tbody>
            {openLines.map((l) => (
              <tr key={l.id}>
                <td>
                  {l.item_code} {l.item_name}
                  <input type="hidden" name="poLineId" value={l.id} />
                </td>
                <td>{l.quantity}</td>
                <td>{l.received_qty}</td>
                <td>
                  <input
                    type="number"
                    step="0.01"
                    name="receivedQty"
                    className="form-control"
                    defaultValue={l.quantity - l.received_qty}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <button type="submit" className="btn btn-primary">
          確認收貨
        </button>
      </form>
    </div>
  );
}
