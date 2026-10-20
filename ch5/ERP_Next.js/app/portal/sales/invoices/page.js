import { listArInvoices } from '@/lib/sales';
import { recordReceiptAction } from '@/app/actions/sales';

export default async function ArInvoicesPage() {
  const invoices = listArInvoices();

  return (
    <div className="py-4">
      <h2>應收發票</h2>
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th>發票號碼</th>
            <th>銷售訂單</th>
            <th>客戶</th>
            <th>金額</th>
            <th>VAT</th>
            <th>已收款</th>
            <th>狀態</th>
            <th>收款</th>
          </tr>
        </thead>
        <tbody>
          {invoices.map((inv) => (
            <tr key={inv.id}>
              <td>{inv.invoice_no}</td>
              <td>{inv.so_no}</td>
              <td>{inv.customer_name}</td>
              <td>{inv.amount.toFixed(2)}</td>
              <td>{inv.vat_amount.toFixed(2)}</td>
              <td>{inv.received.toFixed(2)}</td>
              <td>{inv.status}</td>
              <td>
                {inv.status === 'open' && (
                  <form action={recordReceiptAction} className="d-flex gap-1">
                    <input type="hidden" name="invoiceId" value={inv.id} />
                    <input
                      type="number"
                      step="0.01"
                      name="amount"
                      className="form-control form-control-sm"
                      defaultValue={(inv.amount - inv.received).toFixed(2)}
                      required
                    />
                    <button type="submit" className="btn btn-sm btn-outline-primary text-nowrap">
                      登錄收款
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
