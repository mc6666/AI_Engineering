const COSTING_METHODS = ['fifo', 'lifo', 'weighted_average', 'standard', 'moving_average'];

export default function ItemFormFields({ item }) {
  return (
    <>
      <div className="row">
        <div className="col-md-6 mb-3">
          <label className="form-label">商品名稱</label>
          <input
            type="text"
            name="itemName"
            className="form-control"
            defaultValue={item?.item_name}
            required
          />
        </div>
        <div className="col-md-6 mb-3">
          <label className="form-label">分類</label>
          <input type="text" name="category" className="form-control" defaultValue={item?.category || ''} />
        </div>
      </div>
      <div className="row">
        <div className="col-md-4 mb-3">
          <label className="form-label">計量單位</label>
          <input type="text" name="uom" className="form-control" defaultValue={item?.uom || 'EA'} required />
        </div>
        <div className="col-md-4 mb-3">
          <label className="form-label">成本計算法</label>
          <select name="costingMethod" className="form-select" defaultValue={item?.costing_method || 'weighted_average'}>
            {COSTING_METHODS.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>
        <div className="col-md-4 mb-3">
          <label className="form-label">標準成本</label>
          <input
            type="number"
            step="0.01"
            name="standardCost"
            className="form-control"
            defaultValue={item?.standard_cost ?? 0}
          />
        </div>
      </div>
      <div className="row">
        <div className="col-md-4 mb-3">
          <label className="form-label">再訂購點</label>
          <input
            type="number"
            step="0.01"
            name="reorderPoint"
            className="form-control"
            defaultValue={item?.reorder_point ?? 0}
          />
        </div>
        <div className="col-md-4 mb-3">
          <label className="form-label">安全庫存</label>
          <input
            type="number"
            step="0.01"
            name="safetyStock"
            className="form-control"
            defaultValue={item?.safety_stock ?? 0}
          />
        </div>
        <div className="col-md-4 mb-3">
          <label className="form-label">前置時間（天）</label>
          <input
            type="number"
            name="leadTimeDays"
            className="form-control"
            defaultValue={item?.lead_time_days ?? 0}
          />
        </div>
      </div>
      <div className="form-check mb-2">
        <input
          type="checkbox"
          name="lotManaged"
          className="form-check-input"
          id="lotManaged"
          defaultChecked={Boolean(item?.lot_managed)}
        />
        <label className="form-check-label" htmlFor="lotManaged">
          批號管理
        </label>
      </div>
      <div className="form-check mb-3">
        <input
          type="checkbox"
          name="serialManaged"
          className="form-check-input"
          id="serialManaged"
          defaultChecked={Boolean(item?.serial_managed)}
        />
        <label className="form-check-label" htmlFor="serialManaged">
          序號管理
        </label>
      </div>
      {item && (
        <div className="form-check mb-3">
          <input
            type="checkbox"
            name="isActive"
            className="form-check-input"
            id="isActive"
            defaultChecked={Boolean(item.is_active)}
          />
          <label className="form-check-label" htmlFor="isActive">
            啟用
          </label>
        </div>
      )}
    </>
  );
}
