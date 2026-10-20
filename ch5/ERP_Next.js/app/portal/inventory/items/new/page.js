import { createItemAction } from '@/app/actions/inventory';
import ItemFormFields from '@/app/components/ItemFormFields';

export default async function NewItemPage({ searchParams }) {
  const { error } = await searchParams;

  return (
    <div className="py-4" style={{ maxWidth: 720 }}>
      <h2>新增商品</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form action={createItemAction}>
        <div className="mb-3">
          <label className="form-label">商品代號</label>
          <input type="text" name="itemCode" className="form-control" required />
        </div>
        <ItemFormFields />
        <button type="submit" className="btn btn-primary">
          新增
        </button>
      </form>
    </div>
  );
}
