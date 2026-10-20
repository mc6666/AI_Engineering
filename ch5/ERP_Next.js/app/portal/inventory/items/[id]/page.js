import { notFound } from 'next/navigation';
import { getItem, searchInventory } from '@/lib/inventory';
import { updateItemAction, generateBarcodeAction } from '@/app/actions/inventory';
import ItemFormFields from '@/app/components/ItemFormFields';

export default async function EditItemPage({ params, searchParams }) {
  const { id } = await params;
  const { error } = await searchParams;
  const item = getItem(Number(id));
  if (!item) notFound();
  const stock = searchInventory({ itemCode: item.item_code });

  return (
    <div className="py-4">
      <div className="row">
        <div className="col-md-7">
          <h2>編輯商品：{item.item_code}</h2>
          {error && <div className="alert alert-danger">{error}</div>}
          <form action={updateItemAction}>
            <input type="hidden" name="id" value={item.id} />
            <ItemFormFields item={item} />
            <button type="submit" className="btn btn-primary">
              儲存
            </button>
          </form>

          <div className="mt-4">
            <h5>條碼</h5>
            <p>{item.barcode || '尚未產生條碼'}</p>
            <form action={generateBarcodeAction}>
              <input type="hidden" name="id" value={item.id} />
              <button type="submit" className="btn btn-outline-secondary btn-sm">
                產生條碼
              </button>
            </form>
          </div>
        </div>
        <div className="col-md-5">
          <h5>各倉庫庫存</h5>
          <table className="table table-sm table-bordered">
            <thead>
              <tr>
                <th>倉庫</th>
                <th>批號/序號</th>
                <th>現有</th>
                <th>已預留</th>
                <th>單位成本</th>
                <th>狀態</th>
              </tr>
            </thead>
            <tbody>
              {stock.map((s) => (
                <tr key={s.id}>
                  <td>{s.warehouse_name}</td>
                  <td>{s.lot_number || s.serial_number || '-'}</td>
                  <td>{s.qty_on_hand}</td>
                  <td>{s.qty_reserved}</td>
                  <td>{s.unit_cost.toFixed(2)}</td>
                  <td>{s.status}</td>
                </tr>
              ))}
              {stock.length === 0 && (
                <tr>
                  <td colSpan={6}>尚無庫存紀錄</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
