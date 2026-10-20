import { db, nextDocNo } from './db';

// ---------- Item master ----------
export function listItems({ activeOnly = false } = {}) {
  const where = activeOnly ? 'WHERE is_active = 1' : '';
  return db.prepare(`SELECT * FROM items ${where} ORDER BY item_code`).all();
}

export function getItem(id) {
  return db.prepare('SELECT * FROM items WHERE id = ?').get(id);
}

export function getItemByCode(itemCode) {
  return db.prepare('SELECT * FROM items WHERE item_code = ?').get(itemCode);
}

export function createItem(data) {
  if (!data.itemCode || !data.itemName) throw new Error('Item code and name are required');
  if (getItemByCode(data.itemCode)) throw new Error('Item code already exists');

  const result = db
    .prepare(
      `INSERT INTO items
        (item_code, item_name, category, uom, barcode, lot_managed, serial_managed,
         costing_method, standard_cost, reorder_point, safety_stock, lead_time_days)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    )
    .run(
      data.itemCode,
      data.itemName,
      data.category || null,
      data.uom || 'EA',
      data.barcode || null,
      data.lotManaged ? 1 : 0,
      data.serialManaged ? 1 : 0,
      data.costingMethod || 'weighted_average',
      data.standardCost || 0,
      data.reorderPoint || 0,
      data.safetyStock || 0,
      data.leadTimeDays || 0
    );
  return result.lastInsertRowid;
}

export function updateItem(id, data) {
  const item = getItem(id);
  if (!item) throw new Error('Item not found');
  db.prepare(
    `UPDATE items SET item_name = ?, category = ?, uom = ?, barcode = ?, lot_managed = ?,
       serial_managed = ?, costing_method = ?, standard_cost = ?, reorder_point = ?,
       safety_stock = ?, lead_time_days = ?, is_active = ?
     WHERE id = ?`
  ).run(
    data.itemName ?? item.item_name,
    data.category ?? item.category,
    data.uom ?? item.uom,
    data.barcode ?? item.barcode,
    data.lotManaged !== undefined ? (data.lotManaged ? 1 : 0) : item.lot_managed,
    data.serialManaged !== undefined ? (data.serialManaged ? 1 : 0) : item.serial_managed,
    data.costingMethod ?? item.costing_method,
    data.standardCost ?? item.standard_cost,
    data.reorderPoint ?? item.reorder_point,
    data.safetyStock ?? item.safety_stock,
    data.leadTimeDays ?? item.lead_time_days,
    data.isActive !== undefined ? (data.isActive ? 1 : 0) : item.is_active,
    id
  );
}

export function deleteItem(id) {
  const used = db.prepare('SELECT COUNT(*) AS n FROM stock WHERE item_id = ? AND qty_on_hand != 0').get(id);
  if (used.n > 0) throw new Error('Cannot delete an item that still has stock on hand');
  db.prepare('DELETE FROM items WHERE id = ?').run(id);
}

// ---------- Warehouses ----------
export function listWarehouses({ activeOnly = false } = {}) {
  const where = activeOnly ? 'WHERE is_active = 1' : '';
  return db.prepare(`SELECT * FROM warehouses ${where} ORDER BY warehouse_code`).all();
}

export function getWarehouse(id) {
  return db.prepare('SELECT * FROM warehouses WHERE id = ?').get(id);
}

export function createWarehouse(data) {
  if (!data.warehouseCode || !data.warehouseName) {
    throw new Error('Warehouse code and name are required');
  }
  const result = db
    .prepare(
      'INSERT INTO warehouses (warehouse_code, warehouse_name, location) VALUES (?, ?, ?)'
    )
    .run(data.warehouseCode, data.warehouseName, data.location || null);
  return result.lastInsertRowid;
}

export function updateWarehouse(id, data) {
  const wh = getWarehouse(id);
  if (!wh) throw new Error('Warehouse not found');
  db.prepare(
    'UPDATE warehouses SET warehouse_name = ?, location = ?, is_active = ? WHERE id = ?'
  ).run(
    data.warehouseName ?? wh.warehouse_name,
    data.location ?? wh.location,
    data.isActive !== undefined ? (data.isActive ? 1 : 0) : wh.is_active,
    id
  );
}

// ---------- Stock helpers ----------
function findStockRow({ itemId, warehouseId, binId, lotNumber, serialNumber }) {
  return db
    .prepare(
      `SELECT * FROM stock
       WHERE item_id = ? AND warehouse_id = ?
         AND ((bin_id IS ?) OR (bin_id = ?))
         AND ((lot_number IS ?) OR (lot_number = ?))
         AND ((serial_number IS ?) OR (serial_number = ?))`
    )
    .get(
      itemId,
      warehouseId,
      binId ?? null,
      binId ?? null,
      lotNumber ?? null,
      lotNumber ?? null,
      serialNumber ?? null,
      serialNumber ?? null
    );
}

function availableWarehouseStock(itemId, warehouseId) {
  return db
    .prepare(
      `SELECT * FROM stock WHERE item_id = ? AND warehouse_id = ? AND status = 'available'
       ORDER BY id ASC`
    )
    .all(itemId, warehouseId);
}

function logTransaction({
  txnType,
  itemId,
  warehouseId,
  lotNumber,
  serialNumber,
  quantity,
  unitCost,
  referenceDoc,
  userId,
  notes,
}) {
  db.prepare(
    `INSERT INTO inventory_transactions
      (txn_no, txn_type, item_id, warehouse_id, lot_number, serial_number, quantity,
       unit_cost, reference_doc, user_id, notes)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
  ).run(
    nextDocNo('TXN'),
    txnType,
    itemId,
    warehouseId,
    lotNumber || null,
    serialNumber || null,
    quantity,
    unitCost || 0,
    referenceDoc || null,
    userId || null,
    notes || null
  );
}

// ---------- Receipt ----------
export function receiveInventory({
  itemId,
  warehouseId,
  binId,
  lotNumber,
  serialNumber,
  expirationDate,
  quantity,
  unitCost,
  referenceDoc,
  userId,
}) {
  if (!(quantity > 0)) throw new Error('Receipt quantity must be greater than zero');
  const item = getItem(itemId);
  if (!item) throw new Error('Item not found');
  if (!getWarehouse(warehouseId)) throw new Error('Warehouse not found');

  const cost = item.costing_method === 'standard' ? item.standard_cost : unitCost ?? 0;

  const txn = db.transaction(() => {
    const existing = findStockRow({ itemId, warehouseId, binId, lotNumber, serialNumber });
    if (existing) {
      const newQty = existing.qty_on_hand + quantity;
      const newCost =
        item.costing_method === 'standard'
          ? item.standard_cost
          : (existing.qty_on_hand * existing.unit_cost + quantity * cost) / newQty;
      db.prepare('UPDATE stock SET qty_on_hand = ?, unit_cost = ?, expiration_date = ? WHERE id = ?').run(
        newQty,
        newCost,
        expirationDate ?? existing.expiration_date,
        existing.id
      );
    } else {
      db.prepare(
        `INSERT INTO stock
          (item_id, warehouse_id, bin_id, lot_number, serial_number, expiration_date, qty_on_hand, unit_cost)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
      ).run(itemId, warehouseId, binId || null, lotNumber || null, serialNumber || null, expirationDate || null, quantity, cost);
    }

    // item.average_cost tracks the weighted-average cost across all warehouses.
    const totals = db
      .prepare('SELECT SUM(qty_on_hand) AS qty, SUM(qty_on_hand * unit_cost) AS value FROM stock WHERE item_id = ?')
      .get(itemId);
    const avgCost = totals.qty > 0 ? totals.value / totals.qty : cost;
    db.prepare('UPDATE items SET average_cost = ? WHERE id = ?').run(avgCost, itemId);

    logTransaction({
      txnType: 'receipt',
      itemId,
      warehouseId,
      lotNumber,
      serialNumber,
      quantity,
      unitCost: cost,
      referenceDoc,
      userId,
    });
  });
  txn();
}

// ---------- Issue ----------
// Consumes stock rows in an order matching the item's costing method (FIFO/LIFO by
// receipt order; other methods just draw down whatever rows exist).
export function issueInventory({ itemId, warehouseId, quantity, referenceDoc, userId, notes }) {
  if (!(quantity > 0)) throw new Error('Issue quantity must be greater than zero');
  const item = getItem(itemId);
  if (!item) throw new Error('Item not found');

  const txn = db.transaction(() => {
    let rows = availableWarehouseStock(itemId, warehouseId).filter(
      (r) => r.qty_on_hand - r.qty_reserved > 0
    );
    if (item.costing_method === 'lifo') rows = rows.reverse();

    const totalAvailable = rows.reduce((sum, r) => sum + (r.qty_on_hand - r.qty_reserved), 0);
    if (totalAvailable < quantity) {
      throw new Error(
        `Insufficient available inventory: requested ${quantity}, available ${totalAvailable}`
      );
    }

    let remaining = quantity;
    for (const row of rows) {
      if (remaining <= 0) break;
      const rowAvailable = row.qty_on_hand - row.qty_reserved;
      const take = Math.min(rowAvailable, remaining);
      db.prepare('UPDATE stock SET qty_on_hand = qty_on_hand - ? WHERE id = ?').run(take, row.id);
      logTransaction({
        txnType: 'issue',
        itemId,
        warehouseId,
        lotNumber: row.lot_number,
        serialNumber: row.serial_number,
        quantity: -take,
        unitCost: row.unit_cost,
        referenceDoc,
        userId,
        notes,
      });
      remaining -= take;
    }
  });
  txn();
}

// ---------- Transfer ----------
export function transferInventory({ itemId, fromWarehouseId, toWarehouseId, quantity, userId, referenceDoc }) {
  if (fromWarehouseId === toWarehouseId) throw new Error('Source and destination warehouse must differ');
  if (!getWarehouse(toWarehouseId)) throw new Error('Destination warehouse not found');

  const txn = db.transaction(() => {
    issueInventory({
      itemId,
      warehouseId: fromWarehouseId,
      quantity,
      referenceDoc,
      userId,
      notes: `Transfer to warehouse #${toWarehouseId}`,
    });
    // Re-tag the issue transaction as a transfer-out for reporting purposes.
    db.prepare(
      `UPDATE inventory_transactions SET txn_type = 'transfer_out'
       WHERE item_id = ? AND warehouse_id = ? AND reference_doc IS ?
       ORDER BY id DESC LIMIT 1`
    ).run(itemId, fromWarehouseId, referenceDoc || null);

    const item = getItem(itemId);
    receiveInventory({
      itemId,
      warehouseId: toWarehouseId,
      quantity,
      unitCost: item.average_cost,
      referenceDoc,
      userId,
    });
    db.prepare(
      `UPDATE inventory_transactions SET txn_type = 'transfer_in'
       WHERE item_id = ? AND warehouse_id = ? AND reference_doc IS ?
       ORDER BY id DESC LIMIT 1`
    ).run(itemId, toWarehouseId, referenceDoc || null);
  });
  txn();
}

// ---------- Reservation ----------
export function reserveInventory({ itemId, warehouseId, quantity, referenceDoc }) {
  if (!(quantity > 0)) throw new Error('Reservation quantity must be greater than zero');
  const rows = availableWarehouseStock(itemId, warehouseId);
  const totalAvailable = rows.reduce((sum, r) => sum + (r.qty_on_hand - r.qty_reserved), 0);
  if (totalAvailable < quantity) {
    throw new Error(`Insufficient available inventory to reserve: available ${totalAvailable}`);
  }

  const txn = db.transaction(() => {
    let remaining = quantity;
    for (const row of rows) {
      if (remaining <= 0) break;
      const rowAvailable = row.qty_on_hand - row.qty_reserved;
      const take = Math.min(rowAvailable, remaining);
      db.prepare('UPDATE stock SET qty_reserved = qty_reserved + ? WHERE id = ?').run(take, row.id);
      logTransaction({
        txnType: 'reservation',
        itemId,
        warehouseId,
        lotNumber: row.lot_number,
        serialNumber: row.serial_number,
        quantity: take,
        referenceDoc,
      });
      remaining -= take;
    }
  });
  txn();
}

export function releaseReservation({ itemId, warehouseId, quantity, referenceDoc }) {
  if (!(quantity > 0)) throw new Error('Release quantity must be greater than zero');
  const rows = db
    .prepare(
      `SELECT * FROM stock WHERE item_id = ? AND warehouse_id = ? AND qty_reserved > 0 ORDER BY id ASC`
    )
    .all(itemId, warehouseId);
  const totalReserved = rows.reduce((sum, r) => sum + r.qty_reserved, 0);
  if (totalReserved < quantity) {
    throw new Error(`Cannot release more than is reserved: reserved ${totalReserved}`);
  }

  const txn = db.transaction(() => {
    let remaining = quantity;
    for (const row of rows) {
      if (remaining <= 0) break;
      const take = Math.min(row.qty_reserved, remaining);
      db.prepare('UPDATE stock SET qty_reserved = qty_reserved - ? WHERE id = ?').run(take, row.id);
      logTransaction({
        txnType: 'release',
        itemId,
        warehouseId,
        lotNumber: row.lot_number,
        serialNumber: row.serial_number,
        quantity: -take,
        referenceDoc,
      });
      remaining -= take;
    }
  });
  txn();
}

// ---------- Adjustment ----------
export function adjustInventory({ itemId, warehouseId, binId, lotNumber, serialNumber, quantityDelta, reason, approvedBy, userId }) {
  if (!quantityDelta) throw new Error('Adjustment quantity must not be zero');
  if (!reason) throw new Error('Adjustment reason is required');
  if (!approvedBy) throw new Error('Adjustment requires an approver');

  const txn = db.transaction(() => {
    const existing = findStockRow({ itemId, warehouseId, binId, lotNumber, serialNumber });
    const currentQty = existing ? existing.qty_on_hand : 0;
    const newQty = currentQty + quantityDelta;
    if (newQty < 0) throw new Error('Adjustment would result in negative stock');

    if (existing) {
      db.prepare('UPDATE stock SET qty_on_hand = ? WHERE id = ?').run(newQty, existing.id);
    } else {
      const item = getItem(itemId);
      db.prepare(
        `INSERT INTO stock (item_id, warehouse_id, bin_id, lot_number, serial_number, qty_on_hand, unit_cost)
         VALUES (?, ?, ?, ?, ?, ?, ?)`
      ).run(itemId, warehouseId, binId || null, lotNumber || null, serialNumber || null, newQty, item.average_cost);
    }

    logTransaction({
      txnType: 'adjustment',
      itemId,
      warehouseId,
      lotNumber,
      serialNumber,
      quantity: quantityDelta,
      userId,
      notes: `${reason} (approved by user #${approvedBy})`,
    });
  });
  txn();
}

// ---------- Cycle count ----------
export function performCycleCount({ warehouseId, method, countedBy, lines }) {
  const txn = db.transaction(() => {
    const countId = db
      .prepare('INSERT INTO cycle_counts (count_no, warehouse_id, method, counted_by) VALUES (?, ?, ?, ?)')
      .run(nextDocNo('CC'), warehouseId, method || 'random', countedBy || null).lastInsertRowid;

    const insertLine = db.prepare(
      `INSERT INTO cycle_count_lines (cycle_count_id, item_id, stock_id, system_qty, counted_qty, variance)
       VALUES (?, ?, ?, ?, ?, ?)`
    );
    for (const line of lines) {
      const stock = db.prepare('SELECT * FROM stock WHERE id = ?').get(line.stockId);
      if (!stock) throw new Error(`Stock row #${line.stockId} not found`);
      insertLine.run(
        countId,
        stock.item_id,
        stock.id,
        stock.qty_on_hand,
        line.countedQty,
        line.countedQty - stock.qty_on_hand
      );
    }
    return countId;
  });
  return txn();
}

export function approveCycleCount(cycleCountId, approvedBy) {
  const count = db.prepare('SELECT * FROM cycle_counts WHERE id = ?').get(cycleCountId);
  if (!count) throw new Error('Cycle count not found');
  if (count.status !== 'open') throw new Error('Cycle count already processed');

  const lines = db.prepare('SELECT * FROM cycle_count_lines WHERE cycle_count_id = ?').all(cycleCountId);

  const txn = db.transaction(() => {
    for (const line of lines) {
      if (line.variance) {
        const stock = db.prepare('SELECT * FROM stock WHERE id = ?').get(line.stock_id);
        adjustInventory({
          itemId: line.item_id,
          warehouseId: count.warehouse_id,
          binId: stock.bin_id,
          lotNumber: stock.lot_number,
          serialNumber: stock.serial_number,
          quantityDelta: line.variance,
          reason: `Cycle count ${count.count_no} variance`,
          approvedBy,
        });
      }
    }
    db.prepare('UPDATE cycle_counts SET status = ?, approved_by = ? WHERE id = ?').run(
      'closed',
      approvedBy,
      cycleCountId
    );
  });
  txn();
}

export function listCycleCounts() {
  return db
    .prepare(
      `SELECT cc.*, w.warehouse_name FROM cycle_counts cc
       JOIN warehouses w ON w.id = cc.warehouse_id
       ORDER BY cc.created_at DESC`
    )
    .all();
}

export function getCycleCount(id) {
  const count = db.prepare('SELECT * FROM cycle_counts WHERE id = ?').get(id);
  if (!count) return null;
  const lines = db
    .prepare(
      `SELECT ccl.*, i.item_code, i.item_name FROM cycle_count_lines ccl
       JOIN items i ON i.id = ccl.item_id WHERE ccl.cycle_count_id = ?`
    )
    .all(id);
  return { ...count, lines };
}

// ---------- Physical inventory ----------
export function performPhysicalCount({ warehouseId, lines }) {
  const txn = db.transaction(() => {
    const piId = db
      .prepare('INSERT INTO physical_inventories (count_no, warehouse_id) VALUES (?, ?)')
      .run(nextDocNo('PI'), warehouseId).lastInsertRowid;

    const insertLine = db.prepare(
      `INSERT INTO physical_inventory_lines (physical_inventory_id, item_id, stock_id, system_qty, counted_qty, variance)
       VALUES (?, ?, ?, ?, ?, ?)`
    );
    for (const line of lines) {
      const stock = db.prepare('SELECT * FROM stock WHERE id = ?').get(line.stockId);
      if (!stock) throw new Error(`Stock row #${line.stockId} not found`);
      insertLine.run(piId, stock.item_id, stock.id, stock.qty_on_hand, line.countedQty, line.countedQty - stock.qty_on_hand);
    }
    return piId;
  });
  return txn();
}

export function completePhysicalCount(physicalInventoryId, approvedBy) {
  const pi = db.prepare('SELECT * FROM physical_inventories WHERE id = ?').get(physicalInventoryId);
  if (!pi) throw new Error('Physical inventory not found');
  if (pi.status !== 'frozen') throw new Error('Physical inventory already processed');

  const lines = db
    .prepare('SELECT * FROM physical_inventory_lines WHERE physical_inventory_id = ?')
    .all(physicalInventoryId);

  const txn = db.transaction(() => {
    for (const line of lines) {
      if (line.variance) {
        const stock = db.prepare('SELECT * FROM stock WHERE id = ?').get(line.stock_id);
        adjustInventory({
          itemId: line.item_id,
          warehouseId: pi.warehouse_id,
          binId: stock.bin_id,
          lotNumber: stock.lot_number,
          serialNumber: stock.serial_number,
          quantityDelta: line.variance,
          reason: `Physical inventory ${pi.count_no} variance`,
          approvedBy,
        });
      }
    }
    db.prepare('UPDATE physical_inventories SET status = ? WHERE id = ?').run('completed', physicalInventoryId);
  });
  txn();
}

export function listPhysicalInventories() {
  return db
    .prepare(
      `SELECT pi.*, w.warehouse_name FROM physical_inventories pi
       JOIN warehouses w ON w.id = pi.warehouse_id ORDER BY pi.created_at DESC`
    )
    .all();
}

export function getPhysicalInventory(id) {
  const pi = db.prepare('SELECT * FROM physical_inventories WHERE id = ?').get(id);
  if (!pi) return null;
  const lines = db
    .prepare(
      `SELECT pil.*, i.item_code, i.item_name FROM physical_inventory_lines pil
       JOIN items i ON i.id = pil.item_id WHERE pil.physical_inventory_id = ?`
    )
    .all(id);
  return { ...pi, lines };
}

// ---------- Barcode ----------
export function generateBarcode(itemId) {
  const item = getItem(itemId);
  if (!item) throw new Error('Item not found');
  // Simple EAN-13-shaped code: not a real GS1 allocation, just a stable, unique value.
  const barcode = `200${String(itemId).padStart(9, '0')}`;
  const checkDigit = computeEan13CheckDigit(barcode);
  const fullBarcode = `${barcode}${checkDigit}`;
  db.prepare('UPDATE items SET barcode = ? WHERE id = ?').run(fullBarcode, itemId);
  return fullBarcode;
}

function computeEan13CheckDigit(code12) {
  const digits = code12.split('').map(Number);
  const sum = digits.reduce((acc, d, i) => acc + d * (i % 2 === 0 ? 1 : 3), 0);
  return (10 - (sum % 10)) % 10;
}

export function scanBarcode(barcode) {
  const item = db.prepare('SELECT * FROM items WHERE barcode = ?').get(barcode);
  if (!item) return null;
  const stockByWarehouse = db
    .prepare(
      `SELECT w.warehouse_name, SUM(s.qty_on_hand) AS qty_on_hand, SUM(s.qty_reserved) AS qty_reserved
       FROM stock s JOIN warehouses w ON w.id = s.warehouse_id
       WHERE s.item_id = ? GROUP BY s.warehouse_id`
    )
    .all(item.id);
  return { item, stockByWarehouse };
}

// ---------- Lot / serial ----------
export function manageLot({ itemId, lotNumber }) {
  return db
    .prepare(
      `SELECT s.*, w.warehouse_name FROM stock s
       JOIN warehouses w ON w.id = s.warehouse_id
       WHERE s.item_id = ? AND s.lot_number = ?`
    )
    .all(itemId, lotNumber);
}

export function manageSerialNumber({ itemId, serialNumber }) {
  const current = db
    .prepare(
      `SELECT s.*, w.warehouse_name FROM stock s
       JOIN warehouses w ON w.id = s.warehouse_id
       WHERE s.item_id = ? AND s.serial_number = ?`
    )
    .get(itemId, serialNumber);
  const history = db
    .prepare(
      `SELECT * FROM inventory_transactions WHERE item_id = ? AND serial_number = ? ORDER BY txn_date`
    )
    .all(itemId, serialNumber);
  return { current: current || null, history };
}

// ---------- Transaction history ----------
export function listTransactions({ type, limit = 100 } = {}) {
  const where = type ? 'WHERE t.txn_type = ?' : '';
  const args = type ? [type, limit] : [limit];
  return db
    .prepare(
      `SELECT t.*, i.item_code, i.item_name, w.warehouse_name
       FROM inventory_transactions t
       JOIN items i ON i.id = t.item_id
       JOIN warehouses w ON w.id = t.warehouse_id
       ${where}
       ORDER BY t.id DESC LIMIT ?`
    )
    .all(...args);
}

// ---------- Valuation / reorder / search / dashboard / reports ----------
export function calculateInventoryValue({ warehouseId, itemId } = {}) {
  const conditions = [];
  const args = [];
  if (warehouseId) {
    conditions.push('s.warehouse_id = ?');
    args.push(warehouseId);
  }
  if (itemId) {
    conditions.push('s.item_id = ?');
    args.push(itemId);
  }
  const where = conditions.length ? `WHERE ${conditions.join(' AND ')}` : '';

  const lines = db
    .prepare(
      `SELECT i.id AS item_id, i.item_code, i.item_name, SUM(s.qty_on_hand) AS qty_on_hand,
              SUM(s.qty_on_hand * s.unit_cost) AS value
       FROM stock s JOIN items i ON i.id = s.item_id
       ${where}
       GROUP BY i.id ORDER BY value DESC`
    )
    .all(...args);
  const totalValue = lines.reduce((sum, l) => sum + l.value, 0);
  return { lines, totalValue };
}

export function generateReorderSuggestion({ warehouseId } = {}) {
  const items = db.prepare('SELECT * FROM items WHERE is_active = 1').all();
  const suggestions = [];
  for (const item of items) {
    const where = warehouseId ? 'AND warehouse_id = ?' : '';
    const args = warehouseId ? [item.id, warehouseId] : [item.id];
    const row = db
      .prepare(
        `SELECT COALESCE(SUM(qty_on_hand - qty_reserved), 0) AS available
         FROM stock WHERE item_id = ? ${where}`
      )
      .get(...args);
    const available = row.available;
    if (available <= item.reorder_point) {
      const suggestedQty = Math.max(item.reorder_point + item.safety_stock - available, 0);
      if (suggestedQty > 0) {
        suggestions.push({
          itemId: item.id,
          itemCode: item.item_code,
          itemName: item.item_name,
          available,
          reorderPoint: item.reorder_point,
          safetyStock: item.safety_stock,
          leadTimeDays: item.lead_time_days,
          suggestedQty,
        });
      }
    }
  }
  return suggestions;
}

export function searchInventory({ itemCode, warehouseId, category, lotNumber, serialNumber } = {}) {
  const conditions = [];
  const args = [];
  if (itemCode) {
    conditions.push('i.item_code LIKE ?');
    args.push(`%${itemCode}%`);
  }
  if (warehouseId) {
    conditions.push('s.warehouse_id = ?');
    args.push(warehouseId);
  }
  if (category) {
    conditions.push('i.category = ?');
    args.push(category);
  }
  if (lotNumber) {
    conditions.push('s.lot_number = ?');
    args.push(lotNumber);
  }
  if (serialNumber) {
    conditions.push('s.serial_number = ?');
    args.push(serialNumber);
  }
  const where = conditions.length ? `WHERE ${conditions.join(' AND ')}` : '';

  return db
    .prepare(
      `SELECT s.*, i.item_code, i.item_name, i.uom, w.warehouse_name
       FROM stock s
       JOIN items i ON i.id = s.item_id
       JOIN warehouses w ON w.id = s.warehouse_id
       ${where}
       ORDER BY i.item_code`
    )
    .all(...args);
}

export function getInventoryDashboard() {
  const { totalValue } = calculateInventoryValue();
  const lowStock = generateReorderSuggestion();
  const damagedQuarantined = db
    .prepare(
      `SELECT status, COUNT(*) AS lines, SUM(qty_on_hand) AS qty
       FROM stock WHERE status IN ('damaged', 'quarantined') GROUP BY status`
    )
    .all();
  const topItemsByValue = calculateInventoryValue().lines.slice(0, 10);
  const warehouseCount = db.prepare('SELECT COUNT(*) AS n FROM warehouses WHERE is_active = 1').get().n;
  const itemCount = db.prepare('SELECT COUNT(*) AS n FROM items WHERE is_active = 1').get().n;

  return {
    totalValue,
    lowStockCount: lowStock.length,
    lowStock,
    damagedQuarantined,
    topItemsByValue,
    warehouseCount,
    itemCount,
  };
}

export function generateInventoryReport({ type, warehouseId } = {}) {
  switch (type) {
    case 'valuation':
      return calculateInventoryValue({ warehouseId });
    case 'low_stock':
      return generateReorderSuggestion({ warehouseId });
    case 'status': {
      const where = warehouseId ? 'WHERE warehouse_id = ?' : '';
      const args = warehouseId ? [warehouseId] : [];
      return db
        .prepare(
          `SELECT status, COUNT(*) AS lines, SUM(qty_on_hand) AS qty FROM stock ${where} GROUP BY status`
        )
        .all(...args);
    }
    case 'turnover': {
      const where = warehouseId ? 'AND t.warehouse_id = ?' : '';
      const args = warehouseId ? [warehouseId] : [];
      return db
        .prepare(
          `SELECT i.item_code, i.item_name,
                  COALESCE(SUM(CASE WHEN t.txn_type = 'issue' THEN -t.quantity ELSE 0 END), 0) AS issued_qty,
                  COALESCE((SELECT SUM(qty_on_hand) FROM stock s WHERE s.item_id = i.id), 0) AS on_hand_qty
           FROM items i
           LEFT JOIN inventory_transactions t ON t.item_id = i.id ${where}
           GROUP BY i.id
           ORDER BY issued_qty DESC`
        )
        .all(...args);
    }
    default:
      throw new Error(`Unknown report type: ${type}`);
  }
}
