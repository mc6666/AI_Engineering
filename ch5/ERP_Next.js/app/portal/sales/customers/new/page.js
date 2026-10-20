import { createCustomerAction } from '@/app/actions/sales';

export default async function NewCustomerPage({ searchParams }) {
  const { error } = await searchParams;

  return (
    <div className="py-4" style={{ maxWidth: 560 }}>
      <h2>新增客戶</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form action={createCustomerAction}>
        <div className="mb-3">
          <label className="form-label">客戶代號</label>
          <input type="text" name="customerCode" className="form-control" required />
        </div>
        <div className="mb-3">
          <label className="form-label">客戶名稱</label>
          <input type="text" name="customerName" className="form-control" required />
        </div>
        <div className="row">
          <div className="col-md-6 mb-3">
            <label className="form-label">信用額度</label>
            <input type="number" step="0.01" name="creditLimit" className="form-control" defaultValue="0" />
          </div>
          <div className="col-md-6 mb-3">
            <label className="form-label">付款條件</label>
            <input type="text" name="paymentTerms" className="form-control" />
          </div>
        </div>
        <div className="mb-3">
          <label className="form-label">出貨地址</label>
          <input type="text" name="shippingAddress" className="form-control" />
        </div>
        <button type="submit" className="btn btn-primary">
          新增
        </button>
      </form>
    </div>
  );
}
