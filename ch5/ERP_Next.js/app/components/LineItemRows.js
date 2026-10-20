// Renders a fixed number of blank line-item rows for order/requisition forms.
// Server Actions filter out rows the user left empty (quantity <= 0).
export default function LineItemRows({ items, warehouses, rowCount = 5, withPrice = false, withWarehouse = false }) {
  return (
    <table className="table table-bordered">
      <thead>
        <tr>
          <th>商品</th>
          {withPrice && <th>說明</th>}
          <th>數量</th>
          {withPrice && <th>單價</th>}
          {withPrice && <th>折扣%</th>}
          {withWarehouse && <th>倉庫</th>}
        </tr>
      </thead>
      <tbody>
        {Array.from({ length: rowCount }).map((_, i) => (
          <tr key={i}>
            <td>
              <select name="itemId" className="form-select">
                <option value="">-</option>
                {items.map((it) => (
                  <option key={it.id} value={it.id}>
                    {it.item_code} - {it.item_name}
                  </option>
                ))}
              </select>
            </td>
            {withPrice && (
              <td>
                <input type="text" name="description" className="form-control" />
              </td>
            )}
            <td>
              <input type="number" step="0.01" name="quantity" className="form-control" defaultValue="0" />
            </td>
            {withPrice && (
              <td>
                <input type="number" step="0.01" name="unitPrice" className="form-control" defaultValue="0" />
              </td>
            )}
            {withPrice && (
              <td>
                <input type="number" step="0.01" name="discount" className="form-control" defaultValue="0" />
              </td>
            )}
            {withWarehouse && (
              <td>
                <select name="warehouseId" className="form-select">
                  <option value="">-</option>
                  {warehouses.map((w) => (
                    <option key={w.id} value={w.id}>
                      {w.warehouse_code}
                    </option>
                  ))}
                </select>
              </td>
            )}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
