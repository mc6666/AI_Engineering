import { listSuppliers } from '@/lib/purchase';
import { listItems, listWarehouses } from '@/lib/inventory';
import { createPurchaseOrderAction } from '@/app/actions/purchase';
import LineItemRows from '@/app/components/LineItemRows';

export default async function NewPurchaseOrderPage({ searchParams }) {
  const { error, prId } = await searchParams;
  const suppliers = listSuppliers({ activeOnly: true });
  const items = listItems({ activeOnly: true });
  const warehouses = listWarehouses({ activeOnly: true });

  return (
    <div className="py-4" style={{ maxWidth: 900 }}>
      <h2>新增採購訂單</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form action={createPurchaseOrderAction}>
        {prId && <input type="hidden" name="prId" value={prId} />}
        <div className="row">
          <div className="col-md-4 mb-3">
            <label className="form-label">供應商</label>
            <select name="supplierId" className="form-select" required>
              {suppliers.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.supplier_code} - {s.supplier_name}
                </option>
              ))}
            </select>
          </div>
          <div className="col-md-4 mb-3">
            <label className="form-label">預計交貨日</label>
            <input type="date" name="requiredDate" className="form-control" />
          </div>
          <div className="col-md-4 mb-3">
            <label className="form-label">付款條件</label>
            <input type="text" name="paymentTerms" className="form-control" />
          </div>
        </div>
        <div className="mb-3">
          <label className="form-label">收貨地址</label>
          <input type="text" name="shippingAddress" className="form-control" />
        </div>
        <LineItemRows items={items} warehouses={warehouses} withPrice withWarehouse />
        <button type="submit" className="btn btn-primary">
          建立採購訂單
        </button>
      </form>
    </div>
  );
}
