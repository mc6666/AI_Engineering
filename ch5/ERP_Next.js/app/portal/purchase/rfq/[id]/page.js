import { notFound } from 'next/navigation';
import { getRFQ } from '@/lib/purchase';
import { listSuppliers } from '@/lib/purchase';
import { listItems } from '@/lib/inventory';
import { sendRFQAction, recordQuotationAction } from '@/app/actions/purchase';

export default async function RFQDetailPage({ params }) {
  const { id } = await params;
  const rfq = getRFQ(Number(id));
  if (!rfq) notFound();
  const suppliers = listSuppliers({ activeOnly: true });
  const items = listItems({ activeOnly: true });
  const bestSupplierId = rfq.comparison[0]?.supplierId;

  return (
    <div className="py-4">
      <h2>詢價單：{rfq.rfq_no}</h2>
      <p>狀態：{rfq.status} ｜ 報價截止日：{rfq.quote_due_date || '-'}</p>

      <div className="row">
        <div className="col-md-6">
          <h5>已邀請供應商</h5>
          <ul className="list-group mb-3">
            {rfq.suppliers.map((s) => (
              <li key={s.id} className="list-group-item d-flex justify-content-between">
                <span>{s.supplier_name}</span>
                <span className="badge text-bg-secondary">{s.status}</span>
              </li>
            ))}
            {rfq.suppliers.length === 0 && <li className="list-group-item">尚未邀請供應商</li>}
          </ul>

          <h6>邀請供應商</h6>
          <form action={sendRFQAction} className="mb-4">
            <input type="hidden" name="rfqId" value={rfq.id} />
            {suppliers.map((s) => (
              <div className="form-check" key={s.id}>
                <input type="checkbox" name="supplierIds" value={s.id} className="form-check-input" id={`sup-${s.id}`} />
                <label className="form-check-label" htmlFor={`sup-${s.id}`}>
                  {s.supplier_name}
                </label>
              </div>
            ))}
            <button type="submit" className="btn btn-outline-primary btn-sm mt-2">
              發送詢價
            </button>
          </form>

          <h6>登錄供應商報價</h6>
          <form action={recordQuotationAction}>
            <input type="hidden" name="rfqId" value={rfq.id} />
            <div className="mb-2">
              <select name="supplierId" className="form-select" required>
                {rfq.suppliers.map((s) => (
                  <option key={s.supplier_id} value={s.supplier_id}>
                    {s.supplier_name}
                  </option>
                ))}
              </select>
            </div>
            <div className="mb-2">
              <select name="itemId" className="form-select" required>
                {items.map((it) => (
                  <option key={it.id} value={it.id}>
                    {it.item_code} - {it.item_name}
                  </option>
                ))}
              </select>
            </div>
            <div className="row g-2">
              <div className="col-6">
                <input type="number" step="0.01" name="unitPrice" className="form-control" placeholder="單價" required />
              </div>
              <div className="col-6">
                <input type="number" name="leadTimeDays" className="form-control" placeholder="交期(天)" />
              </div>
              <div className="col-6">
                <input type="text" name="paymentTerms" className="form-control" placeholder="付款條件" />
              </div>
              <div className="col-6">
                <input type="number" step="0.01" name="freightCost" className="form-control" placeholder="運費" />
              </div>
            </div>
            <button type="submit" className="btn btn-outline-primary btn-sm mt-2">
              登錄報價
            </button>
          </form>
        </div>

        <div className="col-md-6">
          <h5>比價分析</h5>
          <table className="table table-bordered">
            <thead>
              <tr>
                <th>供應商</th>
                <th>總成本</th>
                <th>平均交期</th>
                <th>評等</th>
              </tr>
            </thead>
            <tbody>
              {rfq.comparison.map((c) => (
                <tr key={c.supplierId} className={c.supplierId === bestSupplierId ? 'table-success' : ''}>
                  <td>{c.supplierName}</td>
                  <td>{c.totalCost.toFixed(2)}</td>
                  <td>{c.avgLeadTime.toFixed(1)}</td>
                  <td>{c.rating}</td>
                </tr>
              ))}
              {rfq.comparison.length === 0 && (
                <tr>
                  <td colSpan={4}>尚無報價資料</td>
                </tr>
              )}
            </tbody>
          </table>
          {bestSupplierId && (
            <p className="text-success">
              建議供應商：{rfq.comparison[0].supplierName}（總成本最低）
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
