import { createSupplierAction } from '@/app/actions/purchase';

export default async function NewSupplierPage({ searchParams }) {
  const { error } = await searchParams;

  return (
    <div className="py-4" style={{ maxWidth: 560 }}>
      <h2>新增供應商</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form action={createSupplierAction}>
        <div className="mb-3">
          <label className="form-label">供應商代號</label>
          <input type="text" name="supplierCode" className="form-control" required />
        </div>
        <div className="mb-3">
          <label className="form-label">供應商名稱</label>
          <input type="text" name="supplierName" className="form-control" required />
        </div>
        <div className="row">
          <div className="col-md-6 mb-3">
            <label className="form-label">付款條件</label>
            <input type="text" name="paymentTerms" className="form-control" placeholder="例如 Net 30" />
          </div>
          <div className="col-md-6 mb-3">
            <label className="form-label">信用額度</label>
            <input type="number" step="0.01" name="creditLimit" className="form-control" defaultValue="0" />
          </div>
        </div>
        <div className="row">
          <div className="col-md-6 mb-3">
            <label className="form-label">聯絡人</label>
            <input type="text" name="contactPerson" className="form-control" />
          </div>
          <div className="col-md-6 mb-3">
            <label className="form-label">電子郵件</label>
            <input type="email" name="email" className="form-control" />
          </div>
        </div>
        <div className="mb-3">
          <label className="form-label">評等（0-5）</label>
          <input type="number" step="0.1" min="0" max="5" name="rating" className="form-control" defaultValue="0" />
        </div>
        <button type="submit" className="btn btn-primary">
          新增
        </button>
      </form>
    </div>
  );
}
