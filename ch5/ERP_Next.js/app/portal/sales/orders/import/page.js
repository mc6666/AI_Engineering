import { importSalesOrdersAction } from '@/app/actions/sales';

export default async function ImportSalesOrdersPage() {
  return (
    <div className="py-4" style={{ maxWidth: 720 }}>
      <h2>匯入銷售訂單</h2>
      <p className="text-muted">
        貼上 CSV 內容（含標題列），每列建立一張單一品項的草稿銷售訂單：
        <br />
        <code>customerCode,itemCode,quantity,unitPrice,warehouseCode</code>
      </p>
      <form action={importSalesOrdersAction}>
        <div className="mb-3">
          <textarea
            name="csv"
            className="form-control"
            rows={10}
            placeholder={'customerCode,itemCode,quantity,unitPrice,warehouseCode\nCUST-001,ITM-001,10,99.5,WH-01'}
            required
          />
        </div>
        <button type="submit" className="btn btn-primary">
          匯入
        </button>
      </form>
    </div>
  );
}
