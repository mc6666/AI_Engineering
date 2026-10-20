import { searchPurchaseOrders } from '@/lib/purchase';
import { processSupplierInvoiceAction } from '@/app/actions/purchase';

export default async function NewSupplierInvoicePage({ searchParams }) {
  const { error, poId } = await searchParams;
  const orders = searchPurchaseOrders({ status: 'received' });

  return (
    <div className="py-4" style={{ maxWidth: 480 }}>
      <h2>登錄供應商發票</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form action={processSupplierInvoiceAction}>
        <div className="mb-3">
          <label className="form-label">採購訂單</label>
          <select name="poId" className="form-select" defaultValue={poId || ''} required>
            <option value="" disabled>
              請選擇
            </option>
            {orders.map((po) => (
              <option key={po.id} value={po.id}>
                {po.po_no} - {po.supplier_name}
              </option>
            ))}
          </select>
        </div>
        <div className="mb-3">
          <label className="form-label">發票號碼</label>
          <input type="text" name="invoiceNo" className="form-control" required />
        </div>
        <div className="mb-3">
          <label className="form-label">發票日期</label>
          <input type="date" name="invoiceDate" className="form-control" required />
        </div>
        <div className="mb-3">
          <label className="form-label">金額</label>
          <input type="number" step="0.01" name="amount" className="form-control" required />
        </div>
        <div className="mb-3">
          <label className="form-label">付款條件</label>
          <input type="text" name="paymentTerms" className="form-control" />
        </div>
        <button type="submit" className="btn btn-primary">
          登錄並進行三方比對
        </button>
      </form>
    </div>
  );
}
