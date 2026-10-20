import { notFound } from 'next/navigation';
import { getCustomer, getCustomerCredit } from '@/lib/sales';
import { updateCustomerAction } from '@/app/actions/sales';

export default async function EditCustomerPage({ params, searchParams }) {
  const { id } = await params;
  const { error } = await searchParams;
  const customer = getCustomer(Number(id));
  if (!customer) notFound();
  const credit = getCustomerCredit(customer.id);

  return (
    <div className="py-4">
      <div className="row">
        <div className="col-md-7">
          <h2>編輯客戶：{customer.customer_code}</h2>
          {error && <div className="alert alert-danger">{error}</div>}
          <form action={updateCustomerAction}>
            <input type="hidden" name="id" value={customer.id} />
            <div className="mb-3">
              <label className="form-label">客戶名稱</label>
              <input type="text" name="customerName" className="form-control" defaultValue={customer.customer_name} required />
            </div>
            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">信用額度</label>
                <input type="number" step="0.01" name="creditLimit" className="form-control" defaultValue={customer.credit_limit} />
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">付款條件</label>
                <input type="text" name="paymentTerms" className="form-control" defaultValue={customer.payment_terms || ''} />
              </div>
            </div>
            <div className="mb-3">
              <label className="form-label">出貨地址</label>
              <input type="text" name="shippingAddress" className="form-control" defaultValue={customer.shipping_address || ''} />
            </div>
            <div className="form-check mb-3">
              <input
                type="checkbox"
                name="isActive"
                className="form-check-input"
                id="isActive"
                defaultChecked={Boolean(customer.is_active)}
              />
              <label className="form-check-label" htmlFor="isActive">
                啟用
              </label>
            </div>
            <button type="submit" className="btn btn-primary">
              儲存
            </button>
          </form>
        </div>
        <div className="col-md-5">
          <h5>信用狀況</h5>
          <ul className="list-group">
            <li className="list-group-item d-flex justify-content-between">
              <span>信用額度</span> <span>{credit.creditLimit}</span>
            </li>
            <li className="list-group-item d-flex justify-content-between">
              <span>應收餘額</span> <span>{credit.arBalance}</span>
            </li>
            <li className="list-group-item d-flex justify-content-between">
              <span>可用額度</span> <span>{credit.availableCredit}</span>
            </li>
            <li className="list-group-item d-flex justify-content-between">
              <span>逾期金額</span> <span>{credit.overdue}</span>
            </li>
            <li className={`list-group-item ${credit.frozen ? 'text-bg-danger' : ''}`}>
              {credit.frozen ? '信用凍結' : '信用正常'}
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
