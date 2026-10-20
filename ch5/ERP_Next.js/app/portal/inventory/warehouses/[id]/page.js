import { notFound } from 'next/navigation';
import { getWarehouse } from '@/lib/inventory';
import { updateWarehouseAction } from '@/app/actions/inventory';

export default async function EditWarehousePage({ params, searchParams }) {
  const { id } = await params;
  const { error } = await searchParams;
  const warehouse = getWarehouse(Number(id));
  if (!warehouse) notFound();

  return (
    <div className="py-4" style={{ maxWidth: 480 }}>
      <h2>編輯倉庫：{warehouse.warehouse_code}</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form action={updateWarehouseAction}>
        <input type="hidden" name="id" value={warehouse.id} />
        <div className="mb-3">
          <label className="form-label">倉庫名稱</label>
          <input
            type="text"
            name="warehouseName"
            className="form-control"
            defaultValue={warehouse.warehouse_name}
            required
          />
        </div>
        <div className="mb-3">
          <label className="form-label">位置</label>
          <input
            type="text"
            name="location"
            className="form-control"
            defaultValue={warehouse.location || ''}
          />
        </div>
        <div className="form-check mb-3">
          <input
            type="checkbox"
            name="isActive"
            className="form-check-input"
            id="isActive"
            defaultChecked={Boolean(warehouse.is_active)}
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
  );
}
