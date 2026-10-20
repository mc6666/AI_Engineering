import { listItems, listWarehouses } from '@/lib/inventory';
import { createRequisitionAction } from '@/app/actions/purchase';
import LineItemRows from '@/app/components/LineItemRows';

export default async function NewRequisitionPage({ searchParams }) {
  const { error } = await searchParams;
  const items = listItems({ activeOnly: true });
  const warehouses = listWarehouses({ activeOnly: true });

  return (
    <div className="py-4" style={{ maxWidth: 760 }}>
      <h2>新增請購單</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form action={createRequisitionAction}>
        <div className="row">
          <div className="col-md-4 mb-3">
            <label className="form-label">部門</label>
            <input type="text" name="department" className="form-control" />
          </div>
          <div className="col-md-4 mb-3">
            <label className="form-label">需求日期</label>
            <input type="date" name="requiredDate" className="form-control" />
          </div>
          <div className="col-md-4 mb-3">
            <label className="form-label">預算代碼</label>
            <input type="text" name="budgetCode" className="form-control" />
          </div>
        </div>
        <div className="mb-3">
          <label className="form-label">採購原因</label>
          <input type="text" name="reason" className="form-control" />
        </div>
        <LineItemRows items={items} warehouses={warehouses} withWarehouse />
        <button type="submit" className="btn btn-primary">
          送出
        </button>
      </form>
    </div>
  );
}
