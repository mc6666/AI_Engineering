import { listCustomers } from '@/lib/sales';
import { listItems, listWarehouses } from '@/lib/inventory';
import { createSalesOrderAction } from '@/app/actions/sales';
import LineItemRows from '@/app/components/LineItemRows';

export default async function NewSalesOrderPage({ searchParams }) {
  const { error } = await searchParams;
  const customers = listCustomers({ activeOnly: true });
  const items = listItems({ activeOnly: true });
  const warehouses = listWarehouses({ activeOnly: true });

  return (
    <div className="py-4" style={{ maxWidth: 900 }}>
      <h2>新增銷售訂單</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form action={createSalesOrderAction}>
        <div className="row">
          <div className="col-md-4 mb-3">
            <label className="form-label">客戶</label>
            <select name="customerId" className="form-select" required>
              {customers.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.customer_code} - {c.customer_name}
                </option>
              ))}
            </select>
          </div>
          <div className="col-md-4 mb-3">
            <label className="form-label">需求交貨日</label>
            <input type="date" name="requiredDate" className="form-control" />
          </div>
          <div className="col-md-4 mb-3">
            <label className="form-label">出貨地址（選填，預設客戶地址）</label>
            <input type="text" name="shippingAddress" className="form-control" />
          </div>
        </div>
        <LineItemRows items={items} warehouses={warehouses} withPrice withWarehouse />
        <button type="submit" className="btn btn-primary">
          建立銷售訂單
        </button>
      </form>
    </div>
  );
}
