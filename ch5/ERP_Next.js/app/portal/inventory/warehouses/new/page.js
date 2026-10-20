import { createWarehouseAction } from '@/app/actions/inventory';

export default async function NewWarehousePage({ searchParams }) {
  const { error } = await searchParams;

  return (
    <div className="py-4" style={{ maxWidth: 480 }}>
      <h2>新增倉庫</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form action={createWarehouseAction}>
        <div className="mb-3">
          <label className="form-label">倉庫代號</label>
          <input type="text" name="warehouseCode" className="form-control" required />
        </div>
        <div className="mb-3">
          <label className="form-label">倉庫名稱</label>
          <input type="text" name="warehouseName" className="form-control" required />
        </div>
        <div className="mb-3">
          <label className="form-label">位置</label>
          <input type="text" name="location" className="form-control" />
        </div>
        <button type="submit" className="btn btn-primary">
          新增
        </button>
      </form>
    </div>
  );
}
