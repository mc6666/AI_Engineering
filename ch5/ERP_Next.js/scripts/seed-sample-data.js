// One-off sample-data generator for the demo database.
// Run with: node scripts/seed-sample-data.js
//
// lib/*.js are ESM modules only runnable through Next.js's bundler (no "type":
// "module" in package.json), so this script re-implements the same stock/costing
// rules from lib/inventory.js directly against better-sqlite3 rather than
// importing them, to keep generated data consistent with what the app produces.

const Database = require('better-sqlite3');
const path = require('node:path');

const DB_PATH = path.join(process.cwd(), 'data', 'erp.db');
const db = new Database(DB_PATH);
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

let docSeq = 0;
function nextDocNo(prefix) {
  const stamp = new Date();
  const y = stamp.getFullYear();
  const m = String(stamp.getMonth() + 1).padStart(2, '0');
  const d = String(stamp.getDate()).padStart(2, '0');
  docSeq += 1;
  return `${prefix}${y}${m}${d}${String(docSeq).padStart(5, '0')}`;
}

function daysAgo(n) {
  const d = new Date(Date.now() - n * 86400000);
  return d.toISOString().slice(0, 19).replace('T', ' ');
}

// ---------- stock helpers (mirrors lib/inventory.js) ----------
function findStockRow({ itemId, warehouseId, binId, lotNumber, serialNumber }) {
  return db
    .prepare(
      `SELECT * FROM stock
       WHERE item_id = ? AND warehouse_id = ?
         AND ((bin_id IS ?) OR (bin_id = ?))
         AND ((lot_number IS ?) OR (lot_number = ?))
         AND ((serial_number IS ?) OR (serial_number = ?))`
    )
    .get(itemId, warehouseId, binId ?? null, binId ?? null, lotNumber ?? null, lotNumber ?? null, serialNumber ?? null, serialNumber ?? null);
}

function logTransaction({ txnType, itemId, warehouseId, lotNumber, serialNumber, quantity, unitCost, referenceDoc, userId, notes, txnDate }) {
  db.prepare(
    `INSERT INTO inventory_transactions
      (txn_no, txn_type, item_id, warehouse_id, lot_number, serial_number, quantity, unit_cost, txn_date, reference_doc, user_id, notes)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
  ).run(nextDocNo('TXN'), txnType, itemId, warehouseId, lotNumber || null, serialNumber || null, quantity, unitCost || 0, txnDate || daysAgo(0), referenceDoc || null, userId || null, notes || null);
}

function receiveInventory({ itemId, warehouseId, binId, lotNumber, serialNumber, expirationDate, quantity, unitCost, referenceDoc, userId, txnDate }) {
  const item = db.prepare('SELECT * FROM items WHERE id = ?').get(itemId);
  const cost = item.costing_method === 'standard' ? item.standard_cost : unitCost ?? 0;

  const existing = findStockRow({ itemId, warehouseId, binId, lotNumber, serialNumber });
  if (existing) {
    const newQty = existing.qty_on_hand + quantity;
    const newCost = item.costing_method === 'standard' ? item.standard_cost : (existing.qty_on_hand * existing.unit_cost + quantity * cost) / newQty;
    db.prepare('UPDATE stock SET qty_on_hand = ?, unit_cost = ?, expiration_date = ? WHERE id = ?').run(newQty, newCost, expirationDate ?? existing.expiration_date, existing.id);
  } else {
    db.prepare(
      `INSERT INTO stock (item_id, warehouse_id, bin_id, lot_number, serial_number, expiration_date, qty_on_hand, unit_cost)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
    ).run(itemId, warehouseId, binId || null, lotNumber || null, serialNumber || null, expirationDate || null, quantity, cost);
  }

  const totals = db.prepare('SELECT SUM(qty_on_hand) AS qty, SUM(qty_on_hand * unit_cost) AS value FROM stock WHERE item_id = ?').get(itemId);
  const avgCost = totals.qty > 0 ? totals.value / totals.qty : cost;
  db.prepare('UPDATE items SET average_cost = ? WHERE id = ?').run(avgCost, itemId);

  logTransaction({ txnType: 'receipt', itemId, warehouseId, lotNumber, serialNumber, quantity, unitCost: cost, referenceDoc, userId, txnDate });
}

function issueInventory({ itemId, warehouseId, quantity, referenceDoc, userId, notes, txnDate }) {
  const item = db.prepare('SELECT * FROM items WHERE id = ?').get(itemId);
  let rows = db.prepare(`SELECT * FROM stock WHERE item_id = ? AND warehouse_id = ? AND status = 'available' ORDER BY id ASC`).all(itemId, warehouseId).filter((r) => r.qty_on_hand - r.qty_reserved > 0);
  if (item.costing_method === 'lifo') rows = rows.reverse();

  let remaining = quantity;
  for (const row of rows) {
    if (remaining <= 0) break;
    const rowAvailable = row.qty_on_hand - row.qty_reserved;
    const take = Math.min(rowAvailable, remaining);
    db.prepare('UPDATE stock SET qty_on_hand = qty_on_hand - ? WHERE id = ?').run(take, row.id);
    logTransaction({ txnType: 'issue', itemId, warehouseId, lotNumber: row.lot_number, serialNumber: row.serial_number, quantity: -take, unitCost: row.unit_cost, referenceDoc, userId, notes, txnDate });
    remaining -= take;
  }
}

function transferInventory({ itemId, fromWarehouseId, toWarehouseId, quantity, userId, referenceDoc, txnDate }) {
  issueInventory({ itemId, warehouseId: fromWarehouseId, quantity, referenceDoc, userId, notes: `Transfer to warehouse #${toWarehouseId}`, txnDate });
  db.prepare(`UPDATE inventory_transactions SET txn_type = 'transfer_out' WHERE item_id = ? AND warehouse_id = ? AND reference_doc IS ? ORDER BY id DESC LIMIT 1`).run(itemId, fromWarehouseId, referenceDoc || null);
  const item = db.prepare('SELECT * FROM items WHERE id = ?').get(itemId);
  receiveInventory({ itemId, warehouseId: toWarehouseId, quantity, unitCost: item.average_cost, referenceDoc, userId, txnDate });
  db.prepare(`UPDATE inventory_transactions SET txn_type = 'transfer_in' WHERE item_id = ? AND warehouse_id = ? AND reference_doc IS ? ORDER BY id DESC LIMIT 1`).run(itemId, toWarehouseId, referenceDoc || null);
}

function reserveInventory({ itemId, warehouseId, quantity, referenceDoc, txnDate }) {
  const rows = db.prepare(`SELECT * FROM stock WHERE item_id = ? AND warehouse_id = ? AND status = 'available' ORDER BY id ASC`).all(itemId, warehouseId);
  let remaining = quantity;
  for (const row of rows) {
    if (remaining <= 0) break;
    const rowAvailable = row.qty_on_hand - row.qty_reserved;
    const take = Math.min(rowAvailable, remaining);
    if (take <= 0) continue;
    db.prepare('UPDATE stock SET qty_reserved = qty_reserved + ? WHERE id = ?').run(take, row.id);
    logTransaction({ txnType: 'reservation', itemId, warehouseId, lotNumber: row.lot_number, serialNumber: row.serial_number, quantity: take, referenceDoc, txnDate });
    remaining -= take;
  }
}

function releaseReservation({ itemId, warehouseId, quantity, referenceDoc, txnDate }) {
  const rows = db.prepare(`SELECT * FROM stock WHERE item_id = ? AND warehouse_id = ? AND qty_reserved > 0 ORDER BY id ASC`).all(itemId, warehouseId);
  let remaining = quantity;
  for (const row of rows) {
    if (remaining <= 0) break;
    const take = Math.min(row.qty_reserved, remaining);
    db.prepare('UPDATE stock SET qty_reserved = qty_reserved - ? WHERE id = ?').run(take, row.id);
    logTransaction({ txnType: 'release', itemId, warehouseId, lotNumber: row.lot_number, serialNumber: row.serial_number, quantity: -take, referenceDoc, txnDate });
    remaining -= take;
  }
}

function adjustInventory({ itemId, warehouseId, binId, lotNumber, serialNumber, quantityDelta, reason, approvedBy, userId, txnDate }) {
  const existing = findStockRow({ itemId, warehouseId, binId, lotNumber, serialNumber });
  const currentQty = existing ? existing.qty_on_hand : 0;
  const newQty = currentQty + quantityDelta;
  if (existing) {
    db.prepare('UPDATE stock SET qty_on_hand = ? WHERE id = ?').run(newQty, existing.id);
  } else {
    const item = db.prepare('SELECT * FROM items WHERE id = ?').get(itemId);
    db.prepare(`INSERT INTO stock (item_id, warehouse_id, bin_id, lot_number, serial_number, qty_on_hand, unit_cost) VALUES (?, ?, ?, ?, ?, ?, ?)`).run(itemId, warehouseId, binId || null, lotNumber || null, serialNumber || null, newQty, item.average_cost);
  }
  logTransaction({ txnType: 'adjustment', itemId, warehouseId, lotNumber, serialNumber, quantity: quantityDelta, userId, notes: `${reason} (approved by user #${approvedBy})`, txnDate });
}

function computeTotal(lines) {
  return lines.reduce((sum, l) => sum + l.quantity * l.unitPrice * (1 - (l.discount || 0) / 100), 0);
}

// ---------- seed ----------
const seed = db.transaction(() => {
  const existingItems = db.prepare('SELECT COUNT(*) AS n FROM items').get().n;
  if (existingItems > 0) {
    console.log('Sample data already present (items table not empty) — aborting to avoid duplicates.');
    return false;
  }

  const adminId = db.prepare("SELECT id FROM users WHERE username = 'admin'").get().id;

  // Warehouses + bins
  const wh1 = db.prepare('INSERT INTO warehouses (warehouse_code, warehouse_name, location) VALUES (?, ?, ?)').run('WH-01', '主倉庫', '台北市內湖區').lastInsertRowid;
  const wh2 = db.prepare('INSERT INTO warehouses (warehouse_code, warehouse_name, location) VALUES (?, ?, ?)').run('WH-02', '北區配送中心', '桃園市龜山區').lastInsertRowid;
  for (const whId of [wh1, wh2]) {
    db.prepare('INSERT INTO bins (warehouse_id, bin_code, zone) VALUES (?, ?, ?)').run(whId, 'A-01', 'A');
    db.prepare('INSERT INTO bins (warehouse_id, bin_code, zone) VALUES (?, ?, ?)').run(whId, 'A-02', 'A');
  }

  // Items
  const insertItem = db.prepare(
    `INSERT INTO items (item_code, item_name, category, uom, costing_method, standard_cost, reorder_point, safety_stock, lead_time_days, lot_managed)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
  );
  const itemDefs = [
    ['ITEM-001', '27吋 LED 顯示器', '電子產品', 'EA', 'weighted_average', 3500, 20, 10, 7, 0],
    ['ITEM-002', '無線滑鼠', '電子產品', 'EA', 'weighted_average', 350, 50, 20, 5, 0],
    ['ITEM-003', '機械式鍵盤', '電子產品', 'EA', 'weighted_average', 1200, 30, 15, 7, 0],
    ['ITEM-004', 'A4 影印紙(一令)', '辦公用品', 'REAM', 'weighted_average', 120, 200, 100, 3, 0],
    ['ITEM-005', '原子筆(一盒12支)', '辦公用品', 'BOX', 'weighted_average', 60, 100, 50, 2, 0],
    ['ITEM-006', '鋼棒 10mm', '原物料', 'KG', 'fifo', 85, 500, 200, 14, 1],
    ['ITEM-007', '鋁板 2mm', '原物料', 'KG', 'fifo', 150, 300, 100, 10, 1],
    ['ITEM-008', '包裝紙箱(大)', '包材', 'EA', 'weighted_average', 25, 1000, 300, 5, 0],
  ];
  const itemIds = {};
  for (const [code, name, category, uom, costing, stdCost, reorder, safety, lead, lot] of itemDefs) {
    const id = insertItem.run(code, name, category, uom, costing, stdCost, reorder, safety, lead, lot).lastInsertRowid;
    itemIds[code] = id;
  }

  // Suppliers
  const insertSupplier = db.prepare(
    `INSERT INTO suppliers (supplier_code, supplier_name, payment_terms, credit_limit, contact_person, email, rating)
     VALUES (?, ?, ?, ?, ?, ?, ?)`
  );
  const supplierIds = {
    'SUP-001': insertSupplier.run('SUP-001', '台灣電子零件股份有限公司', 'Net 30', 2000000, '王經理', 'sales@taiwan-elec.example.com', 4.5).lastInsertRowid,
    'SUP-002': insertSupplier.run('SUP-002', '全球辦公用品有限公司', 'Net 45', 500000, '李小姐', 'sales@global-office.example.com', 4.0).lastInsertRowid,
    'SUP-003': insertSupplier.run('SUP-003', '中鋼原料供應商', 'Net 60', 5000000, '陳協理', 'sales@steel-supply.example.com', 4.8).lastInsertRowid,
    'SUP-004': insertSupplier.run('SUP-004', '永豐包材工業', 'Net 30', 300000, '張先生', 'sales@yongfeng-pack.example.com', 3.9).lastInsertRowid,
  };

  // Customers
  const insertCustomer = db.prepare(
    `INSERT INTO customers (customer_code, customer_name, credit_limit, payment_terms, shipping_address) VALUES (?, ?, ?, ?, ?)`
  );
  const customerIds = {
    'CUS-001': insertCustomer.run('CUS-001', '友立科技股份有限公司', 1000000, 'Net 30', '台北市信義區松仁路100號').lastInsertRowid,
    'CUS-002': insertCustomer.run('CUS-002', '藍海貿易有限公司', 500000, 'Net 30', '新北市板橋區文化路50號').lastInsertRowid,
    'CUS-003': insertCustomer.run('CUS-003', '誠信商行', 300000, 'Net 15', '台中市西屯區台灣大道200號').lastInsertRowid,
    'CUS-004': insertCustomer.run('CUS-004', '永昌五金行', 200000, 'Net 15', '高雄市三民區builderpark路8號').lastInsertRowid,
    'CUS-005': insertCustomer.run('CUS-005', '大立製造廠', 800000, 'Net 45', '桃園市中壢區中央路300號').lastInsertRowid,
  };

  // Opening stock balances
  const opening = [
    ['ITEM-001', wh1, 40, 3400],
    ['ITEM-002', wh1, 120, 320],
    ['ITEM-003', wh1, 60, 1150],
    ['ITEM-004', wh1, 400, 115],
    ['ITEM-005', wh1, 250, 58],
    ['ITEM-006', wh1, 1500, 82],
    ['ITEM-007', wh1, 600, 145],
    ['ITEM-008', wh1, 3000, 24],
    ['ITEM-002', wh2, 40, 320],
    ['ITEM-003', wh2, 20, 1150],
  ];
  for (const [code, whId, qty, cost] of opening) {
    receiveInventory({ itemId: itemIds[code], warehouseId: whId, quantity: qty, unitCost: cost, referenceDoc: 'Opening Balance', userId: adminId, txnDate: daysAgo(30) });
  }

  // ---------- Purchase requisitions ----------
  const pr1 = db.prepare('INSERT INTO purchase_requisitions (pr_no, requester_id, department, required_date, reason, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)')
    .run(nextDocNo('PR'), adminId, '資訊部', daysAgo(-10), '補充顯示器與滑鼠庫存', 'approved', daysAgo(25)).lastInsertRowid;
  db.prepare('INSERT INTO pr_lines (pr_id, item_id, quantity, warehouse_id) VALUES (?, ?, ?, ?)').run(pr1, itemIds['ITEM-001'], 50, wh1);
  db.prepare('INSERT INTO pr_lines (pr_id, item_id, quantity, warehouse_id) VALUES (?, ?, ?, ?)').run(pr1, itemIds['ITEM-002'], 100, wh1);

  const pr2 = db.prepare('INSERT INTO purchase_requisitions (pr_no, requester_id, department, required_date, reason, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)')
    .run(nextDocNo('PR'), adminId, '生產部', daysAgo(-15), '原物料補貨', 'draft', daysAgo(5)).lastInsertRowid;
  db.prepare('INSERT INTO pr_lines (pr_id, item_id, quantity, warehouse_id) VALUES (?, ?, ?, ?)').run(pr2, itemIds['ITEM-006'], 1000, wh1);

  // ---------- RFQ / quotation ----------
  const rfq1 = db.prepare('INSERT INTO rfqs (rfq_no, pr_id, quote_due_date, status, created_at) VALUES (?, ?, ?, ?, ?)')
    .run(nextDocNo('RFQ'), pr1, daysAgo(-5), 'closed', daysAgo(24)).lastInsertRowid;
  db.prepare('INSERT INTO rfq_suppliers (rfq_id, supplier_id, status) VALUES (?, ?, ?)').run(rfq1, supplierIds['SUP-001'], 'responded');
  db.prepare('INSERT INTO quotations (rfq_id, supplier_id, item_id, unit_price, lead_time_days, payment_terms, freight_cost, submitted_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)')
    .run(rfq1, supplierIds['SUP-001'], itemIds['ITEM-001'], 3400, 7, 'Net 30', 500, daysAgo(22));
  db.prepare('INSERT INTO quotations (rfq_id, supplier_id, item_id, unit_price, lead_time_days, payment_terms, freight_cost, submitted_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)')
    .run(rfq1, supplierIds['SUP-001'], itemIds['ITEM-002'], 330, 5, 'Net 30', 200, daysAgo(22));

  // ---------- Purchase orders ----------
  // PO1: fully received + invoiced + payment scheduled
  const po1Lines = [
    { itemId: itemIds['ITEM-001'], description: '27吋 LED 顯示器', quantity: 50, unitPrice: 3400, warehouseId: wh1 },
    { itemId: itemIds['ITEM-002'], description: '無線滑鼠', quantity: 100, unitPrice: 330, warehouseId: wh1 },
  ];
  const po1Total = computeTotal(po1Lines);
  const po1 = db.prepare('INSERT INTO purchase_orders (po_no, supplier_id, pr_id, order_date, required_date, status, total_amount, buyer_id, payment_terms, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)')
    .run(nextDocNo('PO'), supplierIds['SUP-001'], pr1, daysAgo(20), daysAgo(-3), 'received', po1Total, adminId, 'Net 30', daysAgo(20)).lastInsertRowid;
  const po1LineIds = po1Lines.map((l) => db.prepare('INSERT INTO po_lines (po_id, item_id, description, quantity, unit_price, warehouse_id, received_qty) VALUES (?, ?, ?, ?, ?, ?, ?)')
    .run(po1, l.itemId, l.description, l.quantity, l.unitPrice, l.warehouseId, l.quantity).lastInsertRowid);

  const grn1 = db.prepare('INSERT INTO goods_receipts (grn_no, po_id, warehouse_id, received_date, received_by, status) VALUES (?, ?, ?, ?, ?, ?)')
    .run(nextDocNo('GRN'), po1, wh1, daysAgo(15), adminId, 'passed').lastInsertRowid;
  po1Lines.forEach((l, i) => {
    db.prepare(`INSERT INTO grn_lines (grn_id, po_line_id, item_id, received_qty, inspection_result) VALUES (?, ?, ?, ?, 'pass')`)
      .run(grn1, po1LineIds[i], l.itemId, l.quantity);
    receiveInventory({ itemId: l.itemId, warehouseId: wh1, quantity: l.quantity, unitCost: l.unitPrice, referenceDoc: `GRN-line-${grn1}`, userId: adminId, txnDate: daysAgo(15) });
  });

  const inv1 = db.prepare('INSERT INTO supplier_invoices (invoice_no, po_id, supplier_id, invoice_date, amount, payment_terms, matched, status, created_at) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)')
    .run('SINV-1001', po1, supplierIds['SUP-001'], daysAgo(14), po1Total, 'Net 30', 'scheduled', daysAgo(14)).lastInsertRowid;
  db.prepare('INSERT INTO ap_payments (invoice_id, due_date, amount, status) VALUES (?, ?, ?, ?)').run(inv1, daysAgo(-16), po1Total, 'scheduled');

  // PO2: approved, sent, partially received
  const po2Lines = [{ itemId: itemIds['ITEM-006'], description: '鋼棒 10mm', quantity: 1000, unitPrice: 80, warehouseId: wh1 }];
  const po2Total = computeTotal(po2Lines);
  const po2 = db.prepare('INSERT INTO purchase_orders (po_no, supplier_id, pr_id, order_date, required_date, status, total_amount, buyer_id, payment_terms, sent_at, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)')
    .run(nextDocNo('PO'), supplierIds['SUP-003'], pr2, daysAgo(10), daysAgo(-4), 'partially_received', po2Total, adminId, 'Net 60', daysAgo(9), daysAgo(10)).lastInsertRowid;
  const po2Line = db.prepare('INSERT INTO po_lines (po_id, item_id, description, quantity, unit_price, warehouse_id, received_qty) VALUES (?, ?, ?, ?, ?, ?, ?)')
    .run(po2, po2Lines[0].itemId, po2Lines[0].description, po2Lines[0].quantity, po2Lines[0].unitPrice, po2Lines[0].warehouseId, 600).lastInsertRowid;
  const grn2 = db.prepare('INSERT INTO goods_receipts (grn_no, po_id, warehouse_id, received_date, received_by, status) VALUES (?, ?, ?, ?, ?, ?)')
    .run(nextDocNo('GRN'), po2, wh1, daysAgo(6), adminId, 'passed').lastInsertRowid;
  db.prepare(`INSERT INTO grn_lines (grn_id, po_line_id, item_id, received_qty, inspection_result) VALUES (?, ?, ?, ?, 'pass')`).run(grn2, po2Line, po2Lines[0].itemId, 600);
  receiveInventory({ itemId: po2Lines[0].itemId, warehouseId: wh1, quantity: 600, unitCost: po2Lines[0].unitPrice, referenceDoc: `GRN-line-${grn2}`, userId: adminId, txnDate: daysAgo(6) });

  // PO3: draft
  const po3Lines = [
    { itemId: itemIds['ITEM-004'], description: 'A4 影印紙(一令)', quantity: 500, unitPrice: 110, warehouseId: wh1 },
    { itemId: itemIds['ITEM-005'], description: '原子筆(一盒12支)', quantity: 300, unitPrice: 55, warehouseId: wh1 },
  ];
  db.prepare('INSERT INTO purchase_orders (po_no, supplier_id, order_date, status, total_amount, buyer_id, payment_terms, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)')
    .run(nextDocNo('PO'), supplierIds['SUP-002'], daysAgo(2), 'draft', computeTotal(po3Lines), adminId, 'Net 45', daysAgo(2));
  const po3 = db.prepare('SELECT last_insert_rowid() AS id').get().id;
  for (const l of po3Lines) db.prepare('INSERT INTO po_lines (po_id, item_id, description, quantity, unit_price, warehouse_id) VALUES (?, ?, ?, ?, ?, ?)').run(po3, l.itemId, l.description, l.quantity, l.unitPrice, l.warehouseId);

  // PO4: submitted
  const po4Lines = [{ itemId: itemIds['ITEM-008'], description: '包裝紙箱(大)', quantity: 2000, unitPrice: 22, warehouseId: wh1 }];
  db.prepare('INSERT INTO purchase_orders (po_no, supplier_id, order_date, status, total_amount, buyer_id, payment_terms, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)')
    .run(nextDocNo('PO'), supplierIds['SUP-004'], daysAgo(1), 'submitted', computeTotal(po4Lines), adminId, 'Net 30', daysAgo(1));
  const po4 = db.prepare('SELECT last_insert_rowid() AS id').get().id;
  for (const l of po4Lines) db.prepare('INSERT INTO po_lines (po_id, item_id, description, quantity, unit_price, warehouse_id) VALUES (?, ?, ?, ?, ?, ?)').run(po4, l.itemId, l.description, l.quantity, l.unitPrice, l.warehouseId);

  // ---------- Sales orders ----------
  // SO1: draft
  const so1Lines = [
    { itemId: itemIds['ITEM-001'], description: '27吋 LED 顯示器', quantity: 5, unitPrice: 4200, warehouseId: wh1 },
    { itemId: itemIds['ITEM-002'], description: '無線滑鼠', quantity: 10, unitPrice: 450, warehouseId: wh1 },
  ];
  db.prepare('INSERT INTO sales_orders (so_no, order_date, customer_id, status, total_amount, salesperson_id, shipping_address, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)')
    .run(nextDocNo('SO'), daysAgo(3), customerIds['CUS-001'], 'draft', computeTotal(so1Lines), adminId, '台北市信義區松仁路100號', daysAgo(3));
  const so1 = db.prepare('SELECT last_insert_rowid() AS id').get().id;
  for (const l of so1Lines) db.prepare('INSERT INTO so_lines (so_id, item_id, description, quantity, unit_price, warehouse_id) VALUES (?, ?, ?, ?, ?, ?)').run(so1, l.itemId, l.description, l.quantity, l.unitPrice, l.warehouseId);

  // SO2: open (submitted)
  const so2Lines = [{ itemId: itemIds['ITEM-003'], description: '機械式鍵盤', quantity: 8, unitPrice: 1600, warehouseId: wh1 }];
  db.prepare('INSERT INTO sales_orders (so_no, order_date, customer_id, status, total_amount, salesperson_id, shipping_address, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)')
    .run(nextDocNo('SO'), daysAgo(6), customerIds['CUS-002'], 'open', computeTotal(so2Lines), adminId, '新北市板橋區文化路50號', daysAgo(6));
  const so2 = db.prepare('SELECT last_insert_rowid() AS id').get().id;
  for (const l of so2Lines) db.prepare('INSERT INTO so_lines (so_id, item_id, description, quantity, unit_price, warehouse_id) VALUES (?, ?, ?, ?, ?, ?)').run(so2, l.itemId, l.description, l.quantity, l.unitPrice, l.warehouseId);

  // SO3: approved (reserved)
  const so3Lines = [{ itemId: itemIds['ITEM-004'], description: 'A4 影印紙(一令)', quantity: 50, unitPrice: 150, warehouseId: wh1 }];
  db.prepare('INSERT INTO sales_orders (so_no, order_date, customer_id, status, total_amount, salesperson_id, shipping_address, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)')
    .run(nextDocNo('SO'), daysAgo(8), customerIds['CUS-003'], 'approved', computeTotal(so3Lines), adminId, '台中市西屯區台灣大道200號', daysAgo(8));
  const so3 = db.prepare('SELECT last_insert_rowid() AS id').get().id;
  for (const l of so3Lines) db.prepare('INSERT INTO so_lines (so_id, item_id, description, quantity, unit_price, warehouse_id) VALUES (?, ?, ?, ?, ?, ?)').run(so3, l.itemId, l.description, l.quantity, l.unitPrice, l.warehouseId);
  for (const l of so3Lines) reserveInventory({ itemId: l.itemId, warehouseId: l.warehouseId, quantity: l.quantity, referenceDoc: `SO#${so3}`, txnDate: daysAgo(8) });

  // SO4: shipped
  const so4Lines = [
    { itemId: itemIds['ITEM-002'], description: '無線滑鼠', quantity: 20, unitPrice: 450, warehouseId: wh1 },
    { itemId: itemIds['ITEM-005'], description: '原子筆(一盒12支)', quantity: 30, unitPrice: 85, warehouseId: wh1 },
  ];
  db.prepare('INSERT INTO sales_orders (so_no, order_date, customer_id, status, total_amount, salesperson_id, shipping_address, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)')
    .run(nextDocNo('SO'), daysAgo(12), customerIds['CUS-004'], 'shipped', computeTotal(so4Lines), adminId, '高雄市三民區建工路8號', daysAgo(12));
  const so4 = db.prepare('SELECT last_insert_rowid() AS id').get().id;
  const so4LineIds = so4Lines.map((l) => db.prepare('INSERT INTO so_lines (so_id, item_id, description, quantity, unit_price, warehouse_id, shipped_qty) VALUES (?, ?, ?, ?, ?, ?, ?)')
    .run(so4, l.itemId, l.description, l.quantity, l.unitPrice, l.warehouseId, l.quantity).lastInsertRowid);
  db.prepare('INSERT INTO shipments (shipment_no, so_id, tracking_no, carrier, ship_date, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)')
    .run(nextDocNo('SHP'), so4, 'TW1234567890', '黑貓宅急便', daysAgo(10), 'shipped', daysAgo(10));
  for (const l of so4Lines) issueInventory({ itemId: l.itemId, warehouseId: l.warehouseId, quantity: l.quantity, referenceDoc: `SO#${so4}`, userId: adminId, notes: 'Sales shipment', txnDate: daysAgo(10) });

  // SO5: invoiced with partial receipt
  const so5Lines = [{ itemId: itemIds['ITEM-001'], description: '27吋 LED 顯示器', quantity: 10, unitPrice: 4200, warehouseId: wh1 }];
  const so5Total = computeTotal(so5Lines);
  db.prepare('INSERT INTO sales_orders (so_no, order_date, customer_id, status, total_amount, salesperson_id, shipping_address, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)')
    .run(nextDocNo('SO'), daysAgo(18), customerIds['CUS-005'], 'invoiced', so5Total, adminId, '桃園市中壢區中央路300號', daysAgo(18));
  const so5 = db.prepare('SELECT last_insert_rowid() AS id').get().id;
  for (const l of so5Lines) db.prepare('INSERT INTO so_lines (so_id, item_id, description, quantity, unit_price, warehouse_id, shipped_qty) VALUES (?, ?, ?, ?, ?, ?, ?)').run(so5, l.itemId, l.description, l.quantity, l.unitPrice, l.warehouseId, l.quantity);
  db.prepare('INSERT INTO shipments (shipment_no, so_id, tracking_no, carrier, ship_date, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)')
    .run(nextDocNo('SHP'), so5, 'TW9876543210', '新竹物流', daysAgo(16), 'shipped', daysAgo(16));
  for (const l of so5Lines) issueInventory({ itemId: l.itemId, warehouseId: l.warehouseId, quantity: l.quantity, referenceDoc: `SO#${so5}`, userId: adminId, notes: 'Sales shipment', txnDate: daysAgo(16) });
  const vatAmount = (so5Total * 0.05) / 1.05;
  const invSo5 = db.prepare('INSERT INTO ar_invoices (invoice_no, so_id, customer_id, invoice_date, amount, vat_amount, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)')
    .run(nextDocNo('INV'), so5, customerIds['CUS-005'], daysAgo(15), so5Total, vatAmount, 'open', daysAgo(15)).lastInsertRowid;
  db.prepare('UPDATE customers SET ar_balance = ar_balance + ? WHERE id = ?').run(so5Total, customerIds['CUS-005']);
  const partialReceipt = Math.round(so5Total * 0.4);
  db.prepare('INSERT INTO ar_receipts (invoice_id, received_date, amount) VALUES (?, ?, ?)').run(invSo5, daysAgo(5), partialReceipt);
  db.prepare('UPDATE customers SET ar_balance = ar_balance - ? WHERE id = ?').run(partialReceipt, customerIds['CUS-005']);

  // ---------- Standalone inventory movements ----------
  issueInventory({ itemId: itemIds['ITEM-005'], warehouseId: wh1, quantity: 10, referenceDoc: 'Internal use', userId: adminId, notes: '辦公室內部領用', txnDate: daysAgo(4) });
  transferInventory({ itemId: itemIds['ITEM-003'], fromWarehouseId: wh1, toWarehouseId: wh2, quantity: 10, userId: adminId, referenceDoc: 'Stock rebalance', txnDate: daysAgo(2) });
  adjustInventory({ itemId: itemIds['ITEM-007'], warehouseId: wh1, quantityDelta: 50, reason: '盤點發現多餘庫存', approvedBy: adminId, userId: adminId, txnDate: daysAgo(1) });

  // ---------- Cycle count (open) ----------
  const item1Stock = db.prepare('SELECT * FROM stock WHERE item_id = ? AND warehouse_id = ?').get(itemIds['ITEM-001'], wh1);
  const item2Stock = db.prepare('SELECT * FROM stock WHERE item_id = ? AND warehouse_id = ?').get(itemIds['ITEM-002'], wh1);
  const cc1 = db.prepare('INSERT INTO cycle_counts (count_no, warehouse_id, method, status, counted_by, created_at) VALUES (?, ?, ?, ?, ?, ?)')
    .run(nextDocNo('CC'), wh1, 'random', 'open', adminId, daysAgo(1)).lastInsertRowid;
  for (const stock of [item1Stock, item2Stock]) {
    const countedQty = stock.qty_on_hand - 1;
    db.prepare('INSERT INTO cycle_count_lines (cycle_count_id, item_id, stock_id, system_qty, counted_qty, variance) VALUES (?, ?, ?, ?, ?, ?)')
      .run(cc1, stock.item_id, stock.id, stock.qty_on_hand, countedQty, countedQty - stock.qty_on_hand);
  }

  // ---------- Physical inventory (frozen) ----------
  const item7Stock = db.prepare('SELECT * FROM stock WHERE item_id = ? AND warehouse_id = ?').get(itemIds['ITEM-007'], wh1);
  const pi1 = db.prepare('INSERT INTO physical_inventories (count_no, warehouse_id, status, created_at) VALUES (?, ?, ?, ?)')
    .run(nextDocNo('PI'), wh1, 'frozen', daysAgo(0)).lastInsertRowid;
  db.prepare('INSERT INTO physical_inventory_lines (physical_inventory_id, item_id, stock_id, system_qty, counted_qty, variance) VALUES (?, ?, ?, ?, ?, ?)')
    .run(pi1, item7Stock.item_id, item7Stock.id, item7Stock.qty_on_hand, item7Stock.qty_on_hand, 0);

  console.log('Sample data inserted successfully.');
  return true;
});

const inserted = seed();
if (inserted) {
  const tables = ['items', 'warehouses', 'suppliers', 'customers', 'stock', 'purchase_orders', 'sales_orders', 'inventory_transactions'];
  for (const t of tables) {
    const { n } = db.prepare(`SELECT COUNT(*) AS n FROM ${t}`).get();
    console.log(`${t.padEnd(24)} ${n}`);
  }
}
db.close();
