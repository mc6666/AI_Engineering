import Link from 'next/link';
import { listSupplierInvoices } from '@/lib/purchase';
import { schedulePaymentAction } from '@/app/actions/purchase';

export default async function SupplierInvoicesPage({ searchParams }) {
  const { error } = await searchParams;
  const invoices = listSupplierInvoices();

  return (
    <div className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>供應商發票</h2>
        <Link href="/portal/purchase/invoices/new" className="btn btn-primary">
          登錄發票
        </Link>
      </div>
      {error && <div className="alert alert-danger">{error}</div>}
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th>發票號碼</th>
            <th>採購單號</th>
            <th>供應商</th>
            <th>金額</th>
            <th>三方比對</th>
            <th>狀態</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {invoices.map((inv) => (
            <tr key={inv.id}>
              <td>{inv.invoice_no}</td>
              <td>{inv.po_no}</td>
              <td>{inv.supplier_name}</td>
              <td>{inv.amount.toFixed(2)}</td>
              <td>{inv.matched ? '一致' : '差異'}</td>
              <td>{inv.status}</td>
              <td>
                {inv.status === 'matched' && (
                  <form action={schedulePaymentAction} className="d-flex gap-1">
                    <input type="hidden" name="invoiceId" value={inv.id} />
                    <input type="hidden" name="amount" value={inv.amount} />
                    <input type="date" name="dueDate" className="form-control form-control-sm" required />
                    <button type="submit" className="btn btn-sm btn-outline-primary text-nowrap">
                      安排付款
                    </button>
                  </form>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
