import { notFound } from 'next/navigation';
import { getGoodsReceipt } from '@/lib/purchase';
import { qualityInspectionAction, returnToSupplierAction } from '@/app/actions/purchase';

export default async function GoodsReceiptDetailPage({ params }) {
  const { id } = await params;
  const grn = getGoodsReceipt(Number(id));
  if (!grn) notFound();

  return (
    <div className="py-4">
      <h2>收貨單：{grn.grn_no}</h2>
      <p>狀態：{grn.status}</p>
      <table className="table table-bordered">
        <thead>
          <tr>
            <th>商品</th>
            <th>收貨數量</th>
            <th>驗收結果</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {grn.lines.map((l) => (
            <tr key={l.id}>
              <td>
                {l.item_code} {l.item_name}
              </td>
              <td>{l.received_qty}</td>
              <td>{l.inspection_result}</td>
              <td>
                {l.inspection_result === 'pending' ? (
                  <div className="d-flex gap-2 flex-wrap">
                    <form action={qualityInspectionAction}>
                      <input type="hidden" name="grnId" value={grn.id} />
                      <input type="hidden" name="grnLineId" value={l.id} />
                      <input type="hidden" name="result" value="pass" />
                      <button type="submit" className="btn btn-sm btn-success">
                        合格
                      </button>
                    </form>
                    <form action={qualityInspectionAction}>
                      <input type="hidden" name="grnId" value={grn.id} />
                      <input type="hidden" name="grnLineId" value={l.id} />
                      <input type="hidden" name="result" value="fail" />
                      <button type="submit" className="btn btn-sm btn-danger">
                        不合格
                      </button>
                    </form>
                  </div>
                ) : l.inspection_result === 'fail' ? (
                  <form action={returnToSupplierAction} className="d-flex gap-2 align-items-center">
                    <input type="hidden" name="grnId" value={grn.id} />
                    <input type="hidden" name="grnLineId" value={l.id} />
                    <input type="hidden" name="quantity" value={l.received_qty} />
                    <input type="text" name="reason" className="form-control form-control-sm" placeholder="退貨原因" required />
                    <button type="submit" className="btn btn-sm btn-outline-danger text-nowrap">
                      退貨給供應商
                    </button>
                  </form>
                ) : (
                  '-'
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
