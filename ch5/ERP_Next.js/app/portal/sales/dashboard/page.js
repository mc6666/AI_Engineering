import { getSalesDashboard } from '@/lib/sales';

export default async function SalesDashboardPage() {
  const d = getSalesDashboard();

  return (
    <div className="py-4">
      <h2>銷售儀表板</h2>
      <div className="row mt-3">
        <div className="col-md-3">
          <div className="card text-bg-primary mb-3">
            <div className="card-body">
              <div className="fs-4">{d.todayOrders}</div>
              <div>今日訂單數</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-bg-success mb-3">
            <div className="card-body">
              <div className="fs-4">{d.monthSales.toFixed(2)}</div>
              <div>本月銷售額</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-bg-warning mb-3">
            <div className="card-body">
              <div className="fs-4">{d.pendingShipment}</div>
              <div>待出貨訂單</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-bg-secondary mb-3">
            <div className="card-body">
              <div className="fs-4">{d.pendingInvoice}</div>
              <div>待開發票</div>
            </div>
          </div>
        </div>
      </div>
      <div className="row">
        <div className="col-md-3">
          <div className="card text-bg-danger mb-3">
            <div className="card-body">
              <div className="fs-4">{d.cancelledToday}</div>
              <div>今日取消訂單</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-bg-secondary mb-3">
            <div className="card-body">
              <div className="fs-4">{d.totalRevenue.toFixed(2)}</div>
              <div>總營收</div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-bg-secondary mb-3">
            <div className="card-body">
              <div className="fs-4">{d.avgOrderAmount.toFixed(2)}</div>
              <div>平均訂單金額</div>
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-md-6">
          <div className="card mb-3">
            <div className="card-header">前十大客戶</div>
            <div className="card-body p-0">
              <table className="table table-sm mb-0">
                <thead>
                  <tr>
                    <th>客戶</th>
                    <th>金額</th>
                  </tr>
                </thead>
                <tbody>
                  {d.topCustomers.map((c) => (
                    <tr key={c.customer_name}>
                      <td>{c.customer_name}</td>
                      <td>{c.total.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card mb-3">
            <div className="card-header">暢銷商品</div>
            <div className="card-body p-0">
              <table className="table table-sm mb-0">
                <thead>
                  <tr>
                    <th>商品</th>
                    <th>銷售數量</th>
                  </tr>
                </thead>
                <tbody>
                  {d.topItems.map((it) => (
                    <tr key={it.item_code}>
                      <td>
                        {it.item_code} {it.item_name}
                      </td>
                      <td>{it.qty}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
