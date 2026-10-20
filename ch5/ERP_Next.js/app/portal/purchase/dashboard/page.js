import { getProcurementDashboard } from '@/lib/purchase';

export default async function ProcurementDashboardPage() {
  const d = getProcurementDashboard();

  return (
    <div className="py-4">
      <h2>採購儀表板</h2>
      <div className="row mt-3">
        <div className="col-md-4">
          <div className="card text-bg-warning mb-3">
            <div className="card-body">
              <div className="fs-4">{d.openPRs}</div>
              <div>待處理請購單</div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card text-bg-secondary mb-3">
            <div className="card-body">
              <div className="fs-4">{d.openRFQs}</div>
              <div>進行中詢價單</div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card text-bg-danger mb-3">
            <div className="card-body">
              <div className="fs-4">{d.pendingInvoices}</div>
              <div>待處理發票</div>
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-md-6">
          <div className="card mb-3">
            <div className="card-header">採購訂單狀態分佈</div>
            <div className="card-body p-0">
              <table className="table table-sm mb-0">
                <thead>
                  <tr>
                    <th>狀態</th>
                    <th>數量</th>
                    <th>總金額</th>
                  </tr>
                </thead>
                <tbody>
                  {d.posByStatus.map((s) => (
                    <tr key={s.status}>
                      <td>{s.status}</td>
                      <td>{s.n}</td>
                      <td>{(s.total || 0).toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card mb-3">
            <div className="card-header">前五大供應商（採購金額）</div>
            <div className="card-body p-0">
              <table className="table table-sm mb-0">
                <thead>
                  <tr>
                    <th>供應商</th>
                    <th>採購金額</th>
                  </tr>
                </thead>
                <tbody>
                  {d.topSuppliers.map((s) => (
                    <tr key={s.supplier_name}>
                      <td>{s.supplier_name}</td>
                      <td>{s.total_spend.toFixed(2)}</td>
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
