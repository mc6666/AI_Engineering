import { notFound } from 'next/navigation';
import { getSupplier, generateSupplierScorecard } from '@/lib/purchase';
import { updateSupplierAction } from '@/app/actions/purchase';

export default async function EditSupplierPage({ params, searchParams }) {
  const { id } = await params;
  const { error } = await searchParams;
  const supplier = getSupplier(Number(id));
  if (!supplier) notFound();
  const scorecard = generateSupplierScorecard(supplier.id);

  return (
    <div className="py-4">
      <div className="row">
        <div className="col-md-7">
          <h2>編輯供應商：{supplier.supplier_code}</h2>
          {error && <div className="alert alert-danger">{error}</div>}
          <form action={updateSupplierAction}>
            <input type="hidden" name="id" value={supplier.id} />
            <div className="mb-3">
              <label className="form-label">供應商名稱</label>
              <input type="text" name="supplierName" className="form-control" defaultValue={supplier.supplier_name} required />
            </div>
            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">付款條件</label>
                <input type="text" name="paymentTerms" className="form-control" defaultValue={supplier.payment_terms || ''} />
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">信用額度</label>
                <input type="number" step="0.01" name="creditLimit" className="form-control" defaultValue={supplier.credit_limit} />
              </div>
            </div>
            <div className="row">
              <div className="col-md-6 mb-3">
                <label className="form-label">聯絡人</label>
                <input type="text" name="contactPerson" className="form-control" defaultValue={supplier.contact_person || ''} />
              </div>
              <div className="col-md-6 mb-3">
                <label className="form-label">電子郵件</label>
                <input type="email" name="email" className="form-control" defaultValue={supplier.email || ''} />
              </div>
            </div>
            <div className="mb-3">
              <label className="form-label">評等（0-5）</label>
              <input type="number" step="0.1" min="0" max="5" name="rating" className="form-control" defaultValue={supplier.rating} />
            </div>
            <div className="form-check mb-3">
              <input
                type="checkbox"
                name="isActive"
                className="form-check-input"
                id="isActive"
                defaultChecked={Boolean(supplier.is_active)}
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
          <h5>供應商績效評分卡</h5>
          <ul className="list-group">
            <li className="list-group-item d-flex justify-content-between">
              <span>採購訂單數</span> <span>{scorecard.totalPurchaseOrders}</span>
            </li>
            <li className="list-group-item d-flex justify-content-between">
              <span>採購總金額</span> <span>{scorecard.totalSpend.toFixed(2)}</span>
            </li>
            <li className="list-group-item d-flex justify-content-between">
              <span>品質合格率</span>
              <span>{scorecard.qualityPassRate === null ? '-' : `${(scorecard.qualityPassRate * 100).toFixed(1)}%`}</span>
            </li>
            <li className="list-group-item d-flex justify-content-between">
              <span>退貨率</span> <span>{(scorecard.returnRate * 100).toFixed(1)}%</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
